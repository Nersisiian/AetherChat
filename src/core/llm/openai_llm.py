from typing import AsyncIterator, List, Dict, Any, cast
from openai import AsyncOpenAI
from .base import BaseLLM
from ..config import settings

class OpenAILLM(BaseLLM):
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.model_name

    async def agenerate(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        # OpenAI SDK принимает специфичные типы, мы передаём list[dict] через Any
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore[arg-type]
            stream=False
        )
        if hasattr(response, "choices"):
            return response.choices[0].message.content or ""
        return ""

    def astream(self, messages: List[Dict[str, str]]) -> AsyncIterator[str]:
        async def _stream():
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                stream=True
            )
            async for chunk in stream:
                if hasattr(chunk, "choices") and chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
        return _stream()