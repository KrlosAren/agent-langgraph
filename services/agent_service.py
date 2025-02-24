from langchain_openai import ChatOpenAI
from langgraph.graph import END

from entities.agent_type import State


from langgraph.graph import StateGraph



class Agent:

    def __init__(self, llm):
        self._llm = llm
        self._graph_builder = StateGraph(State)

    @classmethod
    def from_open_ai_model(cls, llm) -> "Agent":
        return cls(llm=llm)

    @property
    def llm(self):
        return self._llm

    @property
    def graph_builder(self):
        return self._graph_builder

    def graph_compile(self, memory = None):
        if memory:
            return self.graph_builder.compile(checkpointer=memory)
        
        return self.graph_builder.compile()

    def add_node(self, node_name, node_function):
        self.graph_builder.add_node(node_name, node_function)


def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END
