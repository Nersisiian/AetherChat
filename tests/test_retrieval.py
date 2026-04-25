import pytest
from langchain_core.documents import Document
from src.core.retrieval.hybrid_search import HybridRetriever

@pytest.fixture
def sample_docs():
    return [
        Document(page_content="Кошки спят по 16 часов в день.", metadata={"source": "animals"}),
        Document(page_content="Собаки нуждаются в ежедневных прогулках.", metadata={"source": "animals"}),
        Document(page_content="Python — язык программирования с динамической типизацией.", metadata={"source": "tech"}),
        Document(page_content="FastAPI — современный фреймворк для создания API.", metadata={"source": "tech"}),
    ]

def test_hybrid_retriever_initialization(sample_docs):
    retriever = HybridRetriever(sample_docs)
    assert retriever is not None

def test_index_documents(sample_docs):
    retriever = HybridRetriever(sample_docs)
    retriever.index_documents()
    # Проверяем, что коллекция не пустая (косвенно через retrieve)
    results = retriever.retrieve("собаки")
    assert any("Собаки" in doc.page_content for doc in results)

def test_retrieve_relevance(sample_docs):
    retriever = HybridRetriever(sample_docs)
    retriever.index_documents()
    results = retriever.retrieve("Как долго спят кошки?")
    assert "16 часов" in results[0].page_content

def test_retriever_empty_query(sample_docs):
    retriever = HybridRetriever(sample_docs)
    retriever.index_documents()
    results = retriever.retrieve("")
    # Не должно падать, возвращается что-то (возможно пустой список)
    assert isinstance(results, list)