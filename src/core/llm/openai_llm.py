from typing import AsyncIterator, List, Dict
from openai import AsyncOpenAI
from .base import BaseLLM
from ..config import settings

class OpenAILLM(BaseLLM):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.model_name

    async def agenerate(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False
        )
        return response.choices[0].message.content

    async def astream(self, messages: List[Dict[str, str]]) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content