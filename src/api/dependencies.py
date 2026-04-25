from src.core.retrieval.hybrid_search import HybridRetriever
from src.core.llm.openai_llm import OpenAILLM
from src.core.agent_graph import RAGAgent

_retriever = None
_agent = None

def get_retriever() -> HybridRetriever:
    global _retriever
    if not _retriever:
        raise RuntimeError("Индексация не выполнена. Сначала POST /ingest/documents")
    return _retriever

def get_agent() -> RAGAgent:
    global _agent
    if not _agent:
        _agent = RAGAgent(get_retriever(), OpenAILLM())
    return _agent