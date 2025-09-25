import os
import uuid
import hashlib
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
    AskQuestion,
)
from app.service.qdrant_util import QdrantVectorStore
from app.models.user import (
    User,
    UserPublic,
    UsersPublic,
)
from langchain_community.embeddings import ZhipuAIEmbeddings
from langchain_community.chat_models import ChatZhipuAI
from qdrant_client import QdrantClient


router = APIRouter(tags=["docs"])


client = QdrantClient(url="http://qdrant:6333", api_key=os.getenv("QDRANT_API_KEY", "test_env"))
vector_store = QdrantVectorStore(client, collection_name="knowledge_documents")


# ========= 工具函数 =========
embeddings = ZhipuAIEmbeddings(
    model="embedding-3",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
    dimensions=1024
)


def chunk_text(text: str, max_len: int = 500) -> List[str]:
    """
    CharacterTextSplitter
    基于字符数进行切割。
    RecursiveCharacterTextSplitter
    基于文本结构进行切割，尝试保持段落等较大单元的完整性。
    MarkdownTextSplitter
    基于 Markdown 标题进行切割。
    HTMLTextSplitter
    基于 HTML 标签进行切割。
    RecursiveJSONTextSplitter
    基于 JSON 结构进行切割。
    CodeTextSplitter
    基于代码结构进行切割。
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=max_len, chunk_overlap=100)
    texts = text_splitter.split_text(text)
    return texts


def extract_text_from_file(file_path: str, filename: str) -> str:
    """根据文件类型解析文本"""

    """
    加载器:CSV、文件目录、HTML、JSON、Markdown 及 PDF等。
    """
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


# ========= 路由 =========
class UploadResponse(BaseModel):
    doc_id: uuid.UUID
    name: str
    status: str


def get_file_path_hash(file_path: str) -> str:
    """获取文件的hash值"""
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return file_hash


def get_file_bytes_hash(file_bytes: bytes) -> str:
    """获取文件的hash值"""
    file_hash = hashlib.md5(file_bytes).hexdigest()
    return file_hash


@router.post("/kb/{kb_id}/docs/upload", response_model=UploadResponse)
async def upload_doc(*, session: SessionDep,
                     kb_id: uuid.UUID,
                     file: UploadFile = File(...),
                     current_user: CurrentUser,
                     storage: LocalStorage = Depends(get_local_storage)):
    # 1. 保存文件
    # 异步读取全部 bytes
    contents = await file.read()
    # 获取文件hash值，判断是否存储过
    file_hash = get_file_bytes_hash(contents)
    knowledge_base_file_statement = select(KnowledgeBaseFile)\
        .where(KnowledgeBaseFile.status == 1, KnowledgeBaseFile.file_hash == file_hash).select_from(KnowledgeBaseFile)
    knowledge_base_file_results = session.exec(knowledge_base_file_statement).all()
    if knowledge_base_file_results and len(knowledge_base_file_results) > 0:
        raise HTTPException(status_code=400, detail="文件已存在")
    try:
        file_path = await storage.save_upload_file(file.filename, contents)
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
        file_path = "local:" + file_path
        knowledge_base_file = KnowledgeBaseFile(name=file.filename,
                                                extension=file.filename.split(".")[-1],
                                                size=file.size,
                                                storage=file_path,
                                                knowledge_base_id=kb_id,
                                                status=1,
                                                file_hash=file_hash,
                                                created_by=current_user.id,
                                                updated_by=current_user.id
                                                )
        session.add(knowledge_base_file)
        session.commit()
        session.refresh(knowledge_base_file)
        # 4. 存入向量数据库
        doc_id = knowledge_base_file.id
        """向量化文档并存储到 Qdrant"""
        try:
            embedding = embeddings.embed_documents(chunks)
            # 插入文档
            count = vector_store.insert_document(
                kb_id=kb_id,
                doc_id=doc_id,
                text_chunks=chunks,
                embeddings=embedding  # 这里替换成你的 embed_documents 结果
            )
            print(f"message: 文档 {doc_id} 向量化成功, 共计向量化 {count} 条数据")
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
    knowledge_base_file_statement = select(KnowledgeBaseFile)\
        .where(KnowledgeBaseFile.status == 1, KnowledgeBaseFile.id == doc_id).select_from(KnowledgeBaseFile)
    knowledge_base_file = session.exec(knowledge_base_file_statement).one_or_none()
    """下载文件"""
    if not knowledge_base_file or storage.exists(knowledge_base_file.name):
        raise HTTPException(status_code=404, detail="File not found")

    return storage.get_streaming_response(knowledge_base_file.name)


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


@router.post("/kb/{kb_id}/ask")
async def ask_question(*,
                       question: AskQuestion,
                       kb_id: uuid.UUID,
                       ):
    """查询接口: RAG pipeline"""
    try:
        # 1. 对问题生成 embedding
        query_vec = embeddings.embed_query(question.question)
        # 2. 从 Qdrant 检索
        results = vector_store.search_similar(query_embedding=query_vec, kb_id=kb_id, limit=5)
        llm = ChatZhipuAI(
            model="glm-4",
            temperature=0.5,
        )
        print(f"result: {results}")
        prompt = f"已知内容:\n{results}\n\n问题: {question}\n请基于已知内容回答。"
        answer = llm.invoke(prompt).content
        return {
            "answer": answer
        }
    except Exception as e:
        print(f"message: {str(e)}")
        raise HTTPException(status_code=500, detail="error")

