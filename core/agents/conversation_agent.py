from typing import Dict, Any
from core.agent.base import BaseAgent
from core.llm.base import BaseLLMService
from langgraph.prebuilt import ToolNode,tools_condition
from core.state.state import State
from langgraph.graph import START, END

from core.memory.memory_manager import MemoryManager

class ConversationAgent(BaseAgent):
    """Agent specialized in conversation handling"""

    def __init__(self, llm_service: BaseLLMService,memory_manager: MemoryManager):
        super().__init__()
        self.llm_service = llm_service
        

    def process_message(self, state: State) -> Dict[str, Any]:
        message = self.llm_service.invoke(state["messages"])
        return {"messages": [message]}

    def build_graph(self):
        """Build the conversation graph"""
        self._graph_builder.add_node("chatbot", self.process_message)
        self._add_tool_nodes()
        self._configure_edges()
        return self._graph_builder

    def _add_tool_nodes(self):
        """Add tool nodes to the graph"""
        tool_node = ToolNode(tools=self.llm_service.tools)
        self._graph_builder.add_node("tools", tool_node)

    def _configure_edges(self):
        """Configure graph edges and routing"""
        self._graph_builder.add_conditional_edges(
            "chatbot", tools_condition, {"tools": "tools", END: END}
        )
        self._graph_builder.add_edge("tools", "chatbot")
        self._graph_builder.set_entry_point("chatbot")
        self._graph_builder.add_edge(START, "chatbot")
        self._graph_builder.add_edge("chatbot", END)
