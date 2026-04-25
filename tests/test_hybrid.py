import pytest
from langchain_core.documents import Document
from src.core.retrieval.hybrid_search import HybridRetriever

@pytest.fixture
def sample_docs():
    return [
        Document(page_content="Кошки любят спать.", metadata={}),
        Document(page_content="Собаки любят гулять.", metadata={}),
        Document(page_content="Попугаи говорят.", metadata={}),
    ]

def test_hybrid_retriever(sample_docs):
    retriever = HybridRetriever(sample_docs)
    retriever.index_documents()
    results = retriever.retrieve("Кто говорит?")
    assert len(results) > 0
    assert "Попугаи" in results[0].page_content