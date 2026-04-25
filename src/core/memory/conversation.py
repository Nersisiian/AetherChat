import tiktoken
from typing import List, Dict, Optional
from ..config import settings

class ConversationMemory:
    def __init__(self, max_tokens: Optional[int] = None):
        self.max_tokens: int = max_tokens or settings.max_history_tokens
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.history: List[Dict[str, str]] = []

    def add_user(self, message: str) -> None:
        self.history.append({"role": "user", "content": message})
        self._trim()

    def add_assistant(self, message: str) -> None:
        self.history.append({"role": "assistant", "content": message})
        self._trim()

    def get_history(self) -> List[Dict[str, str]]:
        return self.history.copy()

    def _trim(self) -> None:
        total = 0
        keep: List[Dict[str, str]] = []
        for msg in reversed(self.history):
            tokens = len(self.encoder.encode(msg["content"]))
            if total + tokens > self.max_tokens:
                break
            keep.insert(0, msg)
            total += tokens
        self.history = keep