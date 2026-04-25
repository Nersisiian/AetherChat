import pdfplumber
from langchain_core.documents import Document
import httpx
from bs4 import BeautifulSoup

async def load_pdf(file_path: str) -> list[Document]:
    docs = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                docs.append(Document(page_content=text, metadata={"source": file_path, "page": i}))
    return docs

async def load_web(url: str) -> Document:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "lxml")
        text = soup.get_text(separator="\n")
        return Document(page_content=text, metadata={"source": url, "type": "web"})

def load_markdown(folder: str) -> list[Document]:
    import os
    docs = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.endswith(".md"):
                with open(os.path.join(root, f), "r") as fp:
                    content = fp.read()
                    docs.append(Document(page_content=content, metadata={"source": f}))
    return docs

async def ingest_all(paths: list[str]) -> list[Document]:
    import os
    all_docs = []
    for path in paths:
        if path.endswith(".pdf"):
            all_docs.extend(await load_pdf(path))
        elif path.startswith("http"):
            all_docs.append(await load_web(path))
        elif os.path.isdir(path):
            all_docs.extend(load_markdown(path))
    return all_docs