import pytest
from src.ingestion.chunker import chunk_documents
from langchain_core.documents import Document

@pytest.mark.anyio
async def test_load_pdf():
    pass

def test_chunker():
    docs = [Document(page_content="Hello world. " * 100)]
    chunks = chunk_documents(docs, chunk_size=50, chunk_overlap=10)
    assert len(chunks) > 1
    assert all(len(chunk.page_content) <= 50 for chunk in chunks)