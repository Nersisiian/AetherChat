import json
import asyncio
from src.core.llm.openai_llm import OpenAILLM

async def generate_qa(context: str, num_questions: int = 3):
    llm = OpenAILLM()
    prompt = f"Сгенерируй {num_questions} вопросов и ответов на основе следующего контекста. Верни JSON-массив объектов с ключами 'question' и 'answer'. Контекст:\n{context}"
    messages = [{"role": "user", "content": prompt}]
    resp = await llm.agenerate(messages)
    try:
        qa_pairs = json.loads(resp)
    except Exception:
        qa_pairs = []
    return qa_pairs

async def main():
    from src.ingestion.loader import load_markdown
    docs = load_markdown("./docs")
    all_qa = []
    for doc in docs:
        qas = await generate_qa(doc.page_content, 3)
        all_qa.extend(qas)
    with open("src/evaluation/sample_qa.json", "w") as f:
        json.dump(all_qa, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())