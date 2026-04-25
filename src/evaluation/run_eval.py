# src/evaluation/run_eval.py
from .metrics import faithfulness, rouge_l
from ..core.retrieval.hybrid_search import HybridRetriever
from ..core.llm.openai_llm import OpenAILLM
from ..core.agent_graph import RAGAgent
import json
import asyncio

async def evaluate_sample(agent, sample):
    answer = await agent.arun(sample["question"])
    context = "\n".join([d.page_content for d in agent.retriever.retrieve(sample["question"])])
    return {
        "question": sample["question"],
        "expected": sample["answer"],
        "generated": answer,
        "faithfulness": faithfulness(answer, context),
        "rouge_l": rouge_l(sample["answer"], answer)
    }

async def run_evaluation(dataset_path: str = "src/evaluation/sample_qa.json"):
    with open(dataset_path) as f:
        dataset = json.load(f)
    retriever = HybridRetriever([])  # Документы должны быть проиндексированы заранее
    agent = RAGAgent(retriever, OpenAILLM())
    results = []
    for sample in dataset:
        res = await evaluate_sample(agent, sample)
        results.append(res)
    avg_faith = sum(r["faithfulness"] for r in results) / len(results)
    avg_rouge = sum(r["rouge_l"] for r in results) / len(results)
    return {"per_question": results, "avg_faithfulness": avg_faith, "avg_rouge_l": avg_rouge}