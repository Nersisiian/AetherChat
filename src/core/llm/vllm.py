import httpx
from typing import AsyncIterator, List, Dict
from .base import BaseLLM
from ..config import settings

class VLLMClient(BaseLLM):
    def __init__(self) -> None:
        if settings.llm_provider == "ollama":
            self.base_url = settings.ollama_base_url.rstrip("/") + "/v1"
        else:
            self.base_url = settings.vllm_base_url.rstrip("/") + "/v1"
        self.model = settings.model_name
        self.client = httpx.AsyncClient(timeout=60.0)

    async def agenerate(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        payload = {"model": self.model, "messages": messages, "stream": False}
        response = await self.client.post(f"{self.base_url}/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def astream(self, messages: List[Dict[str, str]]) -> AsyncIterator[str]:
        async def _stream():
            payload = {"model": self.model, "messages": messages, "stream": True}
            async with self.client.stream("POST", f"{self.base_url}/chat/completions", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]
                        if chunk.strip() == "[DONE]":
                            break
                        import json
                        data = json.loads(chunk)
                        delta = data["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
        return _stream()