import pytest
from src.ingestion.loader import load_pdf, load_web, load_markdown, ingest_all
from src.ingestion.chunker import chunk_documents
from langchain_core.documents import Document

@pytest.mark.anyio
async def test_load_pdf():
    # для реального теста нужен PDF файл, можно пропустить
    pass

def test_chunker():
    docs = [Document(page_content="Hello world. " * 100)]
    chunks = chunk_documents(docs, chunk_size=50, chunk_overlap=10)
    assert len(chunks) > 1
    assert all(len(chunk.page_content) <= 50 for chunk in chunks)