from fastapi import APIRouter, UploadFile, File
from typing import List
import aiofiles
import os
from ...ingestion.loader import ingest_all
from ...ingestion.chunker import chunk_documents
from ...core.retrieval.hybrid_search import HybridRetriever

router = APIRouter()

@router.post("/documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    temp_dir = "/tmp/aetherchat_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    paths: List[str] = []
    for file in files:
        filename = file.filename or "temp_file"
        file_path = os.path.join(temp_dir, filename)
        async with aiofiles.open(file_path, 'wb') as out:
            content = await file.read()
            await out.write(content)
        paths.append(file_path)
    docs = await ingest_all(paths)
    chunked = chunk_documents(docs)
    global_retriever: HybridRetriever = HybridRetriever(chunked)
    global_retriever.index_documents()
    import src.api.dependencies as deps
    deps._retriever = global_retriever
    return {"status": "indexed", "chunks": len(chunked)}