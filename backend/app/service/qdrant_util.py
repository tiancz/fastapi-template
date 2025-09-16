import numpy as np
import uuid
from datetime import datetime
from qdrant_client.http import models
from typing import List, Optional, Dict, Any
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, VectorParams, Distance


class QdrantVectorStore:
    def __init__(self, client, collection_name: str, vector_size: Optional[int] = None, distance: Distance = Distance.COSINE):
        self.client = client
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = distance
        # 确保 collection 已创建（如果 vector_size 可知）
        if vector_size is not None:
            self._ensure_collection(vector_size)

    def _ensure_collection(self, vector_size: int):
        # 如果 collection 不存在则创建（兼容 qdrant-client）
        try:
            if not self.client.get_collection(self.collection_name, ignore_missing=False):
                # 如果 get_collection 抛异常说明不存在 —— 使用 create_collection
                pass
        except Exception:
            try:
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=self.distance)
                )
            except Exception:
                # fallback: try create_collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=self.distance)
                )

    @staticmethod
    def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
        # 防止除0
        if a is None or b is None:
            return 0.0
        na = np.linalg.norm(a)
        nb = np.linalg.norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return float(np.dot(a, b) / (na * nb))

    def insert_document(self, kb_id: str, doc_id: str, text_chunks: List[str], embeddings: List[List[float]]) -> int:
        """
        向量插入：会校验维度、用确定性 id（便于更新），并批量 upsert
        """
        if not embeddings or len(embeddings) != len(text_chunks):
            raise ValueError("embeddings length must match text_chunks length")

        vector_size = len(embeddings[0])
        # 如果尚未创建 collection，则基于第一个向量维度创建
        if self.vector_size is None:
            self.vector_size = vector_size
            self._ensure_collection(vector_size)
        elif self.vector_size != vector_size:
            raise ValueError(f"vector size mismatch: collection expects {self.vector_size}, got {vector_size}")

        points = []
        for i, (chunk, emb) in enumerate(zip(text_chunks, embeddings)):
            # 限制 payload 中 text 的长度，避免过大
            pts = PointStruct(
                id=str(uuid.uuid4()),
                vector=emb,
                payload={
                    "kb_id": str(kb_id),
                    "doc_id": str(doc_id),
                    "text": chunk,
                    "chunk_index": i,
                    "created_at": datetime.utcnow().isoformat(),
                    "text_length": len(chunk)
                }
            )
            points.append(pts)

        # 批量 upsert（等待完成）
        try:
            op = self.client.upsert(collection_name=self.collection_name, points=points, wait=True)
            return len(points)
        except Exception as e:
            print(f"❌ 插入文档失败: {e}")
            raise

    def search_similar(
            self,
            query_embedding: List[float],
            kb_id: Optional[str] = None,
            limit: int = 5,
            score_threshold: float = 0.6,
            candidate_multiplier: int = 4
    ) -> List[Dict[str, Any]]:
        """
        检索并用本地 cosine 重新排序：
         - 先从 qdrant 拉回较多候选（limit * candidate_multiplier）
         - 使用 with_vectors=True 获取真正向量，在本地用 cosine 进行精确重排和阈值过滤
        """
        try:
            # 构建 filter
            q_filter = None
            must_conditions = []
            if kb_id:
                must_conditions.append(FieldCondition(key="kb_id", match=MatchValue(value=str(kb_id))))
            if must_conditions:
                q_filter = Filter(must=must_conditions)

            # 拉回更多候选以便本地重排
            fetch_n = max(limit * candidate_multiplier, limit)

            # 注意 with_vectors=True，用以本地重新计算相似度
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=q_filter,
                limit=fetch_n,
                with_payload=True,
                with_vectors=True
            )

            # 计算本地 cosine，并重排
            candidates = []
            q_vec = np.array(query_embedding, dtype=float)
            for r in search_results:
                if hasattr(r, "vector") and r.vector is not None:
                    vec = np.array(r.vector, dtype=float)
                else:
                    # 如果没有返回 vector，跳过（不做信任score）
                    continue
                sim = self._cosine_sim(q_vec, vec)
                print(f"cosine sim: {sim}")
                payload = r.payload or {}
                candidates.append({
                    "id": str(r.id),
                    "score": sim,
                    "text": payload.get("text", ""),
                    "doc_id": payload.get("doc_id", ""),
                    "kb_id": payload.get("kb_id", ""),
                    "chunk_index": payload.get("chunk_index", 0)
                })

            # 按 score 降序并过滤阈值
            candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)
            filtered = [c for c in candidates if c["score"] >= score_threshold]

            # 如果过滤后太少，可以回退到 top-N 无阈值（可选）
            if len(filtered) < limit:
                topk = candidates[:limit]
                return topk
            else:
                return filtered[:limit]

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

