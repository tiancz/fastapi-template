import os
import uuid
import tempfile
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

import openai
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from PyPDF2 import PdfReader

router = APIRouter(prefix="/docs", tags=["docs"])

# ========= 配置 =========
openai.api_key = "YOUR_OPENAI_API_KEY"
qdrant = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "knowledge_base"


# ========= 工具函数 =========
def get_embedding(text: str) -> List[float]:
    """调用 OpenAI embedding API"""
    resp = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding


def chunk_text(text: str, max_len: int = 500) -> List[str]:
    """简单切分文本，避免太长"""
    words = text.split()
    chunks, current = [], []
    for w in words:
        current.append(w)
        if len(" ".join(current)) > max_len:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


def extract_text_from_file(file_path: str, filename: str) -> str:
    """根据文件类型解析文本"""
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(file_path)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
    elif ext in [".md", ".txt"]:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    return text


def insert_doc(kb_id: int, doc_id: str, text_chunks: List[str]):
    """把文档分块存入 Qdrant"""
    points = []
    for chunk in text_chunks:
        embedding = get_embedding(chunk)
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "kb_id": kb_id,
                    "doc_id": doc_id,
                    "text": chunk
                }
            )
        )
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)


# ========= 路由 =========
class UploadResponse(BaseModel):
    doc_id: str
    name: str
    status: str


@router.post("/kb/{kb_id}/docs/upload", response_model=UploadResponse)
async def upload_doc(kb_id: int, file: UploadFile = File(...)):
    # 1. 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # 2. 提取文本
        text = extract_text_from_file(tmp_path, file.filename)
        if not text.strip():
            raise HTTPException(status_code=400, detail="文件内容为空")

        # 3. 切分文本
        chunks = chunk_text(text, max_len=500)

        # 4. 存入向量数据库
        doc_id = str(uuid.uuid4())
        insert_doc(kb_id, doc_id, chunks)

        # 5. 存入文件表
        db.add_file(kb_id, doc_id, file.filename)

        return UploadResponse(doc_id=doc_id, name=file.filename, status="ready")

    finally:
        os.remove(tmp_path)

