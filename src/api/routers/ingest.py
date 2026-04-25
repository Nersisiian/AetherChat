from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import List
import aiofiles
import os
from ...ingestion.loader import ingest_all
from ...ingestion.chunker import chunk_documents
from ...core.retrieval.hybrid_search import HybridRetriever

router = APIRouter()

class IngestURLsRequest(BaseModel):
    urls: List[str]

@router.post("/documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    temp_dir = "/tmp/aetherchat_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    paths = []
    for file in files:
        file_path = os.path.join(temp_dir, file.filename)
        async with aiofiles.open(file_path, 'wb') as out:
            content = await file.read()
            await out.write(content)
        paths.append(file_path)
    docs = await ingest_all(paths)
    chunked = chunk_documents(docs)
    global_retriever = HybridRetriever(chunked)
    global_retriever.index_documents()
    import src.api.dependencies as deps
    deps._retriever = global_retriever
    return {"status": "indexed", "chunks": len(chunked)}