from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct, Distance, VectorParams
from typing import List, Optional, Dict, Any
import uuid
import os
from datetime import datetime


class QdrantVectorStore:
    """Qdrant 向量存储管理器"""

    def __init__(self, url: str = "", api_key: Optional[str] = None):
        self.client = QdrantClient(
            url=url,
            api_key=api_key,
            timeout=30  # 增加超时时间
        )
        self.collection_name = "knowledge_documents"

        # 确保集合存在
        self._ensure_collection()

    def _ensure_collection(self):
        """确保集合存在，如果不存在则创建"""
        try:
            # 检查集合是否存在
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                # 创建新的集合
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1024,  # 根据你的嵌入模型调整维度
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ 创建集合: {self.collection_name}")
            else:
                print(f"✅ 集合已存在: {self.collection_name}")

        except Exception as e:
            print(f"❌ 检查/创建集合失败: {e}")
            raise

    def insert_document(
            self,
            kb_id: str,
            doc_id: str,
            text_chunks: List[str],
            embeddings: Optional[List[List[float]]] = None
    ) -> int:
        """
        把文档分块存入 Qdrant

        Args:
            kb_id: 知识库ID
            doc_id: 文档ID
            text_chunks: 文本块列表
            embeddings: 可选的嵌入向量列表（如果为None则使用默认嵌入）

        Returns:
            插入的点数
        """
        points = []

        for i, chunk in enumerate(text_chunks):
            # 生成嵌入向量（如果没有提供）
            if embeddings and i < len(embeddings):
                embedding = embeddings[i]
            else:
                # 默认嵌入（实际使用时应该替换为真实的嵌入模型）
                embedding = [0.1] * 384  # 384维的默认向量

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "kb_id": str(kb_id),
                    "doc_id": str(doc_id),
                    "text": chunk,
                    "chunk_index": i,
                    "created_at": datetime.now().isoformat(),
                    "text_length": len(chunk)
                }
            )
            points.append(point)

        try:
            # 批量插入点
            operation_info = self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True  # 等待操作完成
            )

            print(f"✅ 成功插入 {len(points)} 个文本块到文档 {doc_id}")
            return len(points)

        except Exception as e:
            print(f"❌ 插入文档失败: {e}")
            raise

    def search_similar(
            self,
            query_embedding: List[float],
            kb_id: Optional[str] = None,
            limit: int = 5,
            score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        搜索相似的文本块

        Args:
            query_embedding: 查询向量
            kb_id: 限制在特定知识库中搜索
            limit: 返回结果数量
            score_threshold: 相似度阈值

        Returns:
            相似文本块列表
        """
        try:
            # 构建过滤条件
            filter_condition = None
            if kb_id:
                filter_condition = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="kb_id",
                            match=models.MatchValue(value=str(kb_id))
                        )
                    ]
                )

            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=filter_condition,
                limit=limit,
                score_threshold=score_threshold
            )

            results = []
            for result in search_results:
                results.append({
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "doc_id": result.payload.get("doc_id", ""),
                    "kb_id": result.payload.get("kb_id", ""),
                    "chunk_index": result.payload.get("chunk_index", 0)
                })

            return results

        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档的所有文本块

        Args:
            doc_id: 文档ID

        Returns:
            是否成功删除
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="doc_id",
                            match=models.MatchValue(value=str(doc_id))
                        )
                    ]
                )
            )
            print(f"✅ 已删除文档 {doc_id} 的所有文本块")
            return True

        except Exception as e:
            print(f"❌ 删除文档失败: {e}")
            return False

    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            print(f"❌ 获取集合信息失败: {e}")
            return {}

    def check_connection(self) -> bool:
        """检查 Qdrant 连接"""
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            print(f"❌ Qdrant 连接失败: {e}")
            return False


# 全局实例（或者使用依赖注入）
qdrant_store = QdrantVectorStore(
    url="http://qdrant:6333",
    api_key=os.getenv("QDRANT_API_KEY", "test_env")
)


def get_vector_store() -> QdrantVectorStore:
    """获取本地存储实例的依赖函数"""
    return qdrant_store

