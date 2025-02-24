from dotenv import load_dotenv
from typing import Annotated

from services.db_service import DbService

from services.agent_service import Agent, route_tools
from services.LLMService import LLMService
from langgraph.prebuilt import ToolNode, tools_condition
from entities.agent_type import State
from tools.BasicToolNode import BasicToolNode
from langgraph.checkpoint.memory import MemorySaver

from langgraph.graph import START, END

from rich import print
import loguru

from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph.types import Command, interrupt
from langchain_core.tools import tool, Tool, StructuredTool, InjectedToolCallId
from langchain_core.messages import ToolMessage

from core.agents.conversation_agent import ConversationAgent
from core.llm.openai_service import OpenAIService

from core.memory.memory_manager import MemoryManager,EnhancedMemorySaver

load_dotenv()


# def stream_graph_updates(graph, user_input: str, config: dict):
#     loguru.logger.debug(f"USER INPUT: {user_input}")
#     for event in graph.stream(
#         {"messages": [{"role": "user", "content": user_input}]}, config
#     ):
#         loguru.logger.debug(f"EVENT: {event}")
#         for value in event.values():
#             print(f"[green]🤖 Assistant: {value['messages'][-1].content} [/green]")


# def stream_graph_updates(graph, user_input: str, config: dict):
#     loguru.logger.debug(f"USER INPUT: {user_input}")

#     try:
#         for event in graph.stream(
#             {"messages": [{"role": "user", "content": user_input}]}, config
#         ):
#             loguru.logger.debug(f"EVENT: {event}")
#             # Si no hay interrupción, mostrar la respuesta normal
#             for value in event.values():
#                 print(f"[green]🤖 Assistant: {value['messages'][-1].content} [/green]")

#     except Exception as e:
#         loguru.logger.error(e)
#         print("[red] ❌ Error en la conversación. [/red]")



# def main():

#     travaly_tool = TavilySearchResults(max_results=2)

#     llm = LLMService.from_openai(model_name="gpt-4o-mini")
#     agent = Agent.from_open_ai_model(llm=llm)

#     llm.add_tool(tool=travaly_tool)

#     llm.bind_tools()

#     def chatbot(state: State):
#         message = llm.invoke(state["messages"])
#         assert len(message.tool_calls) <= 1
#         return {"messages": [message]}

#     graph_builder = agent.graph_builder

#     agent.add_node("chatbot", chatbot)
#     # tool_node = BasicToolNode(tools=[travaly_tool])
#     tool_node = ToolNode(tools=llm.tools)

#     graph_builder.add_node("tools", tool_node)

#     graph_builder.add_conditional_edges(
#         "chatbot", route_tools, {"tools": "tools", END: END}
#     )

#     graph_builder.add_edge("tools", "chatbot")
#     graph_builder.set_entry_point("chatbot")
#     graph_builder.add_edge(START, "chatbot")

#     graph_builder.add_edge("chatbot", END)

#     memory = MemorySaver()
#     graph = agent.graph_compile(memory=memory)

#     config = {"configurable": {"thread_id": "1"}}

#     while True:
#         try:
#             user_input = input("👤 User: ")
#             if user_input.lower() in ["quit", "exit", "q"]:
#                 print("👋 Goodbye!")
#                 break

#             stream_graph_updates(graph, user_input, config)
#         except Exception as err:
#             loguru.logger.error(err)
#             print("[red] ❌ Error en la conversación. [/red]")
#             print("[red] ❌ Reiniciando el chatbot. [/red]")
#             break


# if __name__ == "__main__":
#     main()



def setup_agent():
    # Configurar memoria
    memory_saver = EnhancedMemorySaver(max_messages=100)
    memory_manager = MemoryManager(memory_saver)
    
    # Configurar agente
    llm = LLMService.from_openai(model_name="gpt-4-mini")
    agent = ConversationAgent(
        llm_service=llm,
        memory_manager=memory_manager
    )
    
    # Compilar el grafo con la memoria
    graph = agent.build_graph()
    return graph.compile(checkpointer=memory_saver)

def main():
    graph = setup_agent()
    config = {"configurable": {"thread_id": "1"}}
    
    while True:
        try:
            user_input = input("👤 User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                break
                
            # Procesar mensaje
            for event in graph.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config
            ):
                for value in event.values():
                    print(f"🤖 Assistant: {value['messages'][-1].content}")
                    
        except Exception as err:
            print(f"❌ Error: {err}")
            break