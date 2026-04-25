from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from .retrieval.hybrid_search import HybridRetriever
from .llm.openai_llm import OpenAILLM
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document

class AgentState(TypedDict):
    query: str
    history: List[dict]
    documents: List[Document]
    answer: str
    needs_retrieval: bool

class RAGAgent:
    def __init__(self, retriever: HybridRetriever, llm: OpenAILLM):
        self.retriever = retriever
        self.llm = llm
        self.graph = self._build_graph()

    def _decide_to_retrieve(self, state: AgentState) -> str:
        # По умолчанию всегда идём в retrieve, но можно добавить классификатор
        return "retrieve"

    def _retrieve(self, state: AgentState) -> AgentState:
        docs = self.retriever.retrieve(state["query"])
        state["documents"] = docs
        return state

    async def _generate(self, state: AgentState) -> AgentState:
        context = "\n\n".join([d.page_content for d in state["documents"]])
        system_prompt = (
            "Ты — полезный ассистент. Используй только предоставленный контекст для ответа. "
            "Если не знаешь ответа, скажи, что не знаешь."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            *state["history"],
            {"role": "user", "content": f"Контекст:\n{context}\n\nВопрос: {state['query']}"}
        ]
        response = await self.llm.agenerate(messages)
        state["answer"] = response
        return state

    def _build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("retrieve", self._retrieve)
        builder.add_node("generate", self._generate)
        builder.set_entry_point("retrieve")
        builder.add_edge("retrieve", "generate")
        builder.add_edge("generate", END)
        return builder.compile()

    async def arun(self, query: str, history: list[dict] = None) -> str:
        state = {"query": query, "history": history or [], "documents": [], "answer": ""}
        result = await self.graph.ainvoke(state)
        return result["answer"]

    async def astream(self, query: str, history: list[dict] = None):
        # Для стриминга используем генерацию напрямую, т.к. граф не стримит пошагово.
        state = await self.graph.ainvoke({"query": query, "history": history or [], "documents": [], "answer": ""})
        yield state["answer"]