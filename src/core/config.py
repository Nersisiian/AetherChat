from pydantic_settings import BaseSettings
from typing import Optional, Literal

class Settings(BaseSettings):
    # LLM
    llm_provider: Literal["openai", "vllm", "ollama"] = "openai"
    openai_api_key: Optional[str] = None
    vllm_base_url: str = "http://localhost:8000/v1"
    ollama_base_url: str = "http://localhost:11434"
    model_name: str = "gpt-4o-mini"

    # Embeddings
    embedding_model: str = "BAAI/bge-m3"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    collection_name: str = "aetherchat_docs"

    # Retrieval
    top_k_dense: int = 10
    top_k_sparse: int = 5
    use_rerank: bool = True
    rerank_model: str = "BAAI/bge-reranker-v2-m3"

    # Memory
    max_history_tokens: int = 2000

    # App
    rate_limit: str = "10/minute"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()