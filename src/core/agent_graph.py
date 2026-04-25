from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from .retrieval.hybrid_search import HybridRetriever
from .llm.base import BaseLLM
from .memory.conversation import ConversationMemory

class AgentState(TypedDict):
    query: str
    history: List[dict]
    documents: List[dict]
    answer: str
    needs_retrieval: bool

class RAGAgent:
    def __init__(self, retriever: HybridRetriever, llm: BaseLLM, memory: Optional[ConversationMemory] = None):
        self.retriever = retriever
        self.llm = llm
        self.memory = memory or ConversationMemory()
        self.graph = self._build_graph()

    async def _decide_retrieval(self, state: AgentState) -> str:
        context = "\n".join([d["content"] for d in state.get("documents", [])])
        prompt = (
            f"Вопрос: {state['query']}\n"
            f"История диалога: {state['history']}\n"
            f"Контекст из документов (может быть пустым): {context}\n"
            "Нужно ли выполнить поиск по документам, чтобы ответить на вопрос? Ответь одним словом: да или нет."
        )
        messages = [{"role": "user", "content": prompt}]
        resp = await self.llm.agenerate(messages)
        if "да" in resp.lower():
            return "retrieve"
        return "generate"

    async def _retrieve(self, state: AgentState) -> AgentState:
        docs = self.retriever.retrieve(state["query"])
        state["documents"] = [{"content": d.page_content, "metadata": d.metadata} for d in docs]
        return state

    async def _generate(self, state: AgentState) -> AgentState:
        context = "\n\n".join([d["content"] for d in state["documents"]]) if state["documents"] else "Нет документов."
        system = "Ты полезный ассистент. Отвечай на основе контекста. Не придумывай факты."
        messages: list[dict] = [{"role": "system", "content": system}]
        for turn in state["history"]:
            messages.append(turn)
        messages.append({"role": "user", "content": f"Контекст:\n{context}\n\nВопрос: {state['query']}"})
        answer = await self.llm.agenerate(messages)
        state["answer"] = answer
        return state

    def _build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("retrieve", self._retrieve)
        builder.add_node("generate", self._generate)
        builder.set_conditional_entry_point(
            self._decide_retrieval,
            {"retrieve": "retrieve", "generate": "generate"}
        )
        builder.add_edge("retrieve", "generate")
        builder.add_edge("generate", END)
        return builder.compile()

    async def arun(self, query: str, history: Optional[List[dict]] = None) -> str:
        history = history or []
        state = {"query": query, "history": history, "documents": [], "answer": ""}
        result = await self.graph.ainvoke(state)
        return result["answer"]