"""
Pipeline for ingesting documents into the vector store.
Usage:
    python -m src.ingestion.pipeline --files ./docs/manual.pdf --url https://example.com
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import List

from .loader import load_pdf, load_web, load_markdown, ingest_all
from .chunker import chunk_documents
from ..core.retrieval.hybrid_search import HybridRetriever
from ..core.config import settings


class IngestionPipeline:
    def __init__(self):
        self.documents = []

    async def run(self, files: List[str] = None, urls: List[str] = None, dirs: List[str] = None):
        paths = []
        if files:
            paths.extend(files)
        if urls:
            paths.extend(urls)
        if dirs:
            for d in dirs:
                # Добавляем все md-файлы из папок
                paths.append(str(Path(d)))

        print(f"🔄 Loading {len(paths)} sources...")
        docs = await ingest_all(paths)
        if not docs:
            print("❌ No documents loaded. Exiting.")
            return

        print(f"📄 Loaded {len(docs)} documents. Chunking...")
        chunked = chunk_documents(docs)
        print(f"🧩 Created {len(chunked)} chunks. Indexing into Qdrant...")

        retriever = HybridRetriever(chunked)
        retriever.index_documents()

        # Сохраняем retriever глобально (для доступа через depends)
        import src.api.dependencies as deps
        deps._retriever = retriever
        print("✅ Ingestion complete. Retriever is ready.")


async def main():
    parser = argparse.ArgumentParser(description="Ingest documents into AetherChat")
    parser.add_argument("--files", nargs="*", help="Paths to PDF or Markdown files")
    parser.add_argument("--urls", nargs="*", help="URLs of web pages to ingest")
    parser.add_argument("--dirs", nargs="*", help="Directories with Markdown files")
    args = parser.parse_args()

    if not any([args.files, args.urls, args.dirs]):
        parser.print_help()
        return

    pipeline = IngestionPipeline()
    await pipeline.run(files=args.files, urls=args.urls, dirs=args.dirs)


if __name__ == "__main__":
    asyncio.run(main())