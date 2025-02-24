from abc import ABC, abstractmethod
from typing import List, Optional
from langgraph.graph import StateGraph
from entities.agent_type import State

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self):
        self._graph_builder = StateGraph(State)
    
    @abstractmethod
    def process_message(self, state: State):
        """Process incoming messages"""
        pass
    
    @property
    def graph_builder(self):
        return self._graph_builder