from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Dict

class BaseLLM(ABC):
    @abstractmethod
    async def agenerate(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        ...

    @abstractmethod
    def astream(self, messages: List[Dict[str, str]]) -> AsyncIterator[str]:
        ...