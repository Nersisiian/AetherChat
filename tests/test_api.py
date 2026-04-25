import pytest
from httpx import AsyncClient, ASGITransport
from src.api.main import app
from src.api.dependencies import get_retriever
from langchain_core.documents import Document

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
async def client():
    async def override_get_retriever():
        from src.core.retrieval.hybrid_search import HybridRetriever
        docs = [
            Document(page_content="Тестовая страница.", metadata={})
        ]
        retriever = HybridRetriever(docs)
        retriever.index_documents()
        return retriever

    app.dependency_overrides[get_retriever] = override_get_retriever
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.anyio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.anyio
async def test_chat_endpoint(client):
    await client.post("/api/v1/ingest/documents", files=[])
    response = await client.post("/api/v1/chat/", json={"query": "Что говорят документы?"})
    assert response.status_code == 200
    assert "answer" in response.json()