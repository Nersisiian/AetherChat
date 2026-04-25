from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat, ingest, eval

app = FastAPI(title="AetherChat API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["ingest"])
app.include_router(eval.router, prefix="/api/v1/eval", tags=["eval"])

@app.get("/health")
def health():
    return {"status": "ok"}