# src/api/dependencies.py
from src.core.retrieval.hybrid_search import HybridRetriever
from src.core.llm.openai_llm import OpenAILLM
from src.core.agent_graph import RAGAgent
from src.core.config import settings

# Глобальные синглтоны
_retriever = None
_agent = None

def get_retriever() -> HybridRetriever:
    # Предполагаем, что документы уже загружены и индексированы
    # для демо используем заглушку: вызов load_and_index где-то в startup
    global _retriever
    if not _retriever:
        raise RuntimeError("Индексация не выполнена. Сначала POST /ingest/documents")
    return _retriever

def get_agent() -> RAGAgent:
    global _agent
    if not _agent:
        _agent = RAGAgent(get_retriever(), OpenAILLM())
    return _agent