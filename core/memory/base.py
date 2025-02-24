from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class MemoryItem(BaseModel):
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}
    memory_type: str = "general"


class BaseMemory(ABC):
    @abstractmethod
    def add(self, item: MemoryItem) -> None:
        """Add an item to memory"""
        pass

    @abstractmethod
    def get(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """Retrieve relevant memories"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all memories"""
        pass


class MessageMemory(BaseModel):
    """Estructura para almacenar mensajes en memoria"""

    content: str
    role: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}
