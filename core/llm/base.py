from abc import ABC, abstractmethod
from typing import List
from langchain_core.tools import Tool


class BaseLLMService(ABC):
    """Base class for LLM services"""

    def __init__(self):
        self._tools: List[Tool] = []

    @abstractmethod
    def invoke(self, prompt):
        """Invoke the language model"""
        pass

    @property
    def tools(self) -> List[Tool]:
        return self._tools
