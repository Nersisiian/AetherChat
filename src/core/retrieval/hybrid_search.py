from typing import List, Dict, Tuple
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_huggingface import HuggingFaceEmbeddings
from ..config import settings

class HybridRetriever:
    def __init__(self, documents: List[Document]):
        self.documents = documents
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"}
        )
        self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
        self.client.recreate_collection(
            collection_name=settings.collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=settings.collection_name,
            embedding=self.embedding_model
        )
        self._bm25_retriever = None
        self._reranker = None
        if settings.use_rerank:
            self._init_reranker()

    def _init_reranker(self):
        try:
            from FlagEmbedding import FlagReranker
            self._reranker = FlagReranker(settings.rerank_model, use_fp16=True)
        except ImportError:
            print("Warning: FlagEmbedding not installed. Reranker disabled.")
            self._reranker = None

    def _get_bm25(self):
        if not self._bm25_retriever:
            self._bm25_retriever = BM25Retriever.from_documents(self.documents)
            self._bm25_retriever.k = settings.top_k_sparse
        return self._bm25_retriever

    def index_documents(self):
        self.vector_store.add_documents(self.documents)

    def retrieve(self, query: str) -> List[Document]:
        # Получаем результаты от BM25 и Dense ретриверов
        bm25 = self._get_bm25()
        bm25_docs = bm25.invoke(query)  # каждый doc уже содержит поле page_content и metadata
        dense_docs = self.vector_store.as_retriever(
            search_kwargs={"k": settings.top_k_dense}
        ).invoke(query)

        # Присваиваем взвешенные очки: позиция 0 = наивысший рейтинг
        # Веса: BM25 - 0.3, Dense - 0.7
        doc_score: Dict[str, float] = {}
        doc_map: Dict[str, Document] = {}

        def add_docs(docs: List[Document], weight: float):
            for i, doc in enumerate(docs):
                doc_id = doc.page_content + str(doc.metadata)  # простой идентификатор
                score = weight * (1.0 / (i + 1))  # позиционная оценка
                if doc_id in doc_score:
                    doc_score[doc_id] += score
                else:
                    doc_score[doc_id] = score
                    doc_map[doc_id] = doc

        add_docs(bm25_docs, 0.3)
        add_docs(dense_docs, 0.7)

        # Сортируем по убыванию суммарного счёта
        sorted_ids = sorted(doc_score, key=doc_score.get, reverse=True)
        candidates = [doc_map[doc_id] for doc_id in sorted_ids[:5]]

        # Если есть реранкер, применяем его к топ-кандидатам
        if self._reranker and len(candidates) > 1:
            pairs = [[query, doc.page_content] for doc in candidates]
            scores = self._reranker.compute_score(pairs)
            scored_docs = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
            return [doc for doc, _ in scored_docs[:5]]
        return candidates