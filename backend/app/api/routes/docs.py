import os
import uuid
from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from sqlmodel import col, delete, func, select

from pydantic import BaseModel
from app.storage.local_storage import LocalStorage, get_local_storage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models.knowledge_base_file import (
    KnowledgeBaseFile,
    KnowledgeBaseFileCreate,
    KnowledgeBaseFileUpdate,
    KnowledgeBaseFilePublic,
    KnowledgeBaseFilesPublic,
)
from app.service.qdrant_util import QdrantVectorStore, get_vector_store
from app.models.user import (
    User,
    UserPublic,
    UsersPublic,
)


router = APIRouter(tags=["docs"])

# ========= 工具函数 =========
# def get_embedding(text: str) -> List[float]:
#     """调用 OpenAI embedding API"""
#     resp = openai.embeddings.create(
#         model="text-embedding-3-small",
#         input=text
#     )
#     return resp.data[0].embedding


def chunk_text(text: str, max_len: int = 500) -> List[str]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=max_len, chunk_overlap=0)
    texts = text_splitter.split_text(text)
    return texts


def extract_text_from_file(file_path: str, filename: str) -> str:
    """根据文件类型解析文本"""
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        text = "\n".join([page.page_content or "" for page in docs])
    elif ext in [".md", ".txt"]:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    return text


# def insert_doc(kb_id: int, doc_id: str, text_chunks: List[str]):
#     """把文档分块存入 Qdrant"""
#     points = []
#     for chunk in text_chunks:
#         # embedding = get_embedding(chunk)
#         embedding = [1, 0.01]
#         points.append(
#             PointStruct(
#                 id=str(uuid.uuid4()),
#                 vector=embedding,
#                 payload={
#                     "kb_id": kb_id,
#                     "doc_id": doc_id,
#                     "text": chunk
#                 }
#             )
#         )
#     qdrant.upsert(collection_name=COLLECTION_NAME, points=points)


# ========= 路由 =========
class UploadResponse(BaseModel):
    doc_id: uuid.UUID
    name: str
    status: str


@router.post("/kb/{kb_id}/docs/upload", response_model=UploadResponse)
async def upload_doc(*, session: SessionDep,
                     kb_id: uuid.UUID,
                     file: UploadFile = File(...),
                     current_user: CurrentUser,
                     vector_store: QdrantVectorStore = Depends(get_vector_store),
                     storage: LocalStorage = Depends(get_local_storage)):
    # 1. 保存文件
    try:
        file_path = await storage.save_upload_file(file.filename, file)
        print("message: File uploaded successfully, path:" + file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    try:
        # 2. 提取文本
        text = extract_text_from_file(file_path, file.filename)
        if not text.strip():
            raise HTTPException(status_code=400, detail="文件内容为空")

        # 3. 切分文本
        chunks = chunk_text(text, max_len=500)

        # 4. 存入文件表
        knowledge_base_file = KnowledgeBaseFile(name=file.filename,
                                                extension=file.filename.split(".")[-1],
                                                size=file.size,
                                                storage=file_path,
                                                knowledge_base_id=kb_id,
                                                status=1,
                                                created_by=current_user.id,
                                                updated_by=current_user.id
                                                )
        session.add(knowledge_base_file)
        session.commit()
        session.refresh(knowledge_base_file)

        # 4. 存入向量数据库
        doc_id = knowledge_base_file.id
        # insert_doc(kb_id, doc_id, chunks)

        """向量化文档并存储到 Qdrant"""
        try:
            count = vector_store.insert_document(
                kb_id=kb_id,
                doc_id=doc_id,
                text_chunks=chunks
            )

            # return {
            #     "message": "文档向量化成功",
            #     "chunks_count": count,
            #     "doc_id": doc_id
            # }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"向量化失败: {str(e)}")


        return UploadResponse(doc_id=doc_id, name=file.filename, status="ready")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/docs/download/{doc_id}")
async def download_file(
        *, session: SessionDep,
        doc_id: uuid.UUID,
        storage: LocalStorage = Depends(get_local_storage)
):
    # 查询document表
    knowledge_base_file = session.get(KnowledgeBaseFile, doc_id)
    filename = knowledge_base_file.name
    """下载文件"""
    if not storage.exists(filename):
        raise HTTPException(status_code=404, detail="File not found")

    return storage.get_streaming_response(filename)


@router.get("/kb/{kb_id}/docs", response_model=KnowledgeBaseFilesPublic)
async def list_files(
        *, session: SessionDep,
        kb_id: uuid.UUID,
        skip: int = 0, limit: int = 100
):
    """查询对应知识库下的文件"""
    # 查询有效数据 status = 1
    count_statement = select(func.count())\
        .where(KnowledgeBaseFile.status == 1, KnowledgeBaseFile.knowledge_base_id == kb_id)\
        .select_from(KnowledgeBaseFile)
    count = session.exec(count_statement).one()

    # 关联查询
    statement = (
        select(KnowledgeBaseFile, User.full_name.label("creator_name"))
        .join(User, KnowledgeBaseFile.created_by == User.id)
        .where(col(KnowledgeBaseFile.status) == 1, KnowledgeBaseFile.knowledge_base_id == kb_id)
        .offset(skip)
        .limit(limit)
    )
    results = session.exec(statement).all()
    # 处理结果
    knowledge_base_files = [
        {
            **kb.dict(),
            "owner": username
        }
        for kb, username in results
    ]
    return KnowledgeBaseFilesPublic(data=knowledge_base_files, count=count)



@router.delete("/docs/{doc_id}")
async def delete_file(
        *, session: SessionDep,
        doc_id: uuid.UUID,
        storage: LocalStorage = Depends(get_local_storage)
):
    knowledge_base_file = session.get(KnowledgeBaseFile, doc_id)
    filename = knowledge_base_file.name
    """删除文件"""
    if await storage.delete(filename):
        # 修改数据库状态
        session.query(KnowledgeBaseFile).filter(KnowledgeBaseFile.name == filename).update({"status": 0})
        session.commit()
        session.refresh(knowledge_base_file)
        return {"message": "File deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="File not found")


@router.get("/docs/{doc_id}/info")
async def get_file_info(
        *, session: SessionDep,
        doc_id: uuid.UUID,
):
    knowledge_base_file = session.get(KnowledgeBaseFile, doc_id)
    """获取文件信息"""
    if not knowledge_base_file:
        raise HTTPException(status_code=404, detail="File not found")

    return {
        "filename": knowledge_base_file.name,
        "size": knowledge_base_file.size,
        "exists": True
    }


@router.get("/doc/text_split")
async def text_split(size: int):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=0)
    document = "This is a test file. This is a test file. This is a test file. This is a test file. This is a test file. This is a test file. This is a test file. This is a test file. This is a test file. This is a test file. This is a test file. This is a test file. This is a test file. This"
    texts = text_splitter.split_text(document)
    return {
        "texts": texts,
        "exists": True
    }


@router.get("/doc/load_pdf")
async def load_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    return {
        "docs": docs
    }


@router.get("/doc/cur_path")
async def cur_path():
    print("=== 使用 os 模块 ===")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"当前文件路径: {os.path.abspath(__file__)}")
    return {
        "cur": os.getcwd(),
        "cur_file": os.path.abspath(__file__)
    }


