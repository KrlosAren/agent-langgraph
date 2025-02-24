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


load_dotenv()


# def stream_graph_updates(graph, user_input: str, config: dict):
#     loguru.logger.debug(f"USER INPUT: {user_input}")
#     for event in graph.stream(
#         {"messages": [{"role": "user", "content": user_input}]}, config
#     ):
#         loguru.logger.debug(f"EVENT: {event}")
#         for value in event.values():
#             print(f"[green]🤖 Assistant: {value['messages'][-1].content} [/green]")


def stream_graph_updates(graph, user_input: str, config: dict):
    loguru.logger.debug(f"USER INPUT: {user_input}")

    try:
        for event in graph.stream(
            {"messages": [{"role": "user", "content": user_input}]}, config
        ):
            loguru.logger.debug(f"EVENT: {event}")

            # Verificar si el evento es una interrupción
            if "__interrupt__" in event:
                interruption = event["__interrupt__"]  # Esto es una tupla
                if isinstance(interruption, tuple):
                    interruption_data = interruption[
                        0
                    ].value  # Extraer el valor correcto
                else:
                    interruption_data = (
                        interruption.value
                    )  # Por seguridad, si cambia el formato

                print(f"🛑 Interrupción detectada: {interruption_data['query']}")
                
                ## response for AI:
                breakpoint()

                # Solicitar entrada manual para continuar el flujo
                human_response = input("👤 User : ")

                # Reanudar la ejecución con la respuesta humana
                command: Command = Command(resume={"data": human_response})

                # Reenvía el comando al grafo
                for new_event in graph.stream(command, config):
                    if "messages" in new_event:
                        print(
                            f"[green]🤖 Assistant: {new_event['messages'][-1].content} [/green]"
                        )
                        loguru.logger.warning(new_event)
                return  # Salir después de manejar la interrupción

            # Si no hay interrupción, mostrar la respuesta normal
            for value in event.values():
                print(f"[green]🤖 Assistant: {value['messages'][-1].content} [/green]")

    except Exception as e:
        loguru.logger.error(e)
        print("[red] ❌ Error en la conversación. [/red]")

        print("[red] ❌ Error en la conversación. [/red]")


@tool
def human_assistance_tool(query: str):
    """Request assistance from a human."""
    # Detener el flujo hasta que el usuario proporcione una respuesta manualmente
    human_response =  interrupt({"query": query})
    return human_response["data"]


def main():

    memory = MemorySaver()

    travaly_tool = TavilySearchResults(max_results=2)

    llm = LLMService.from_openai(model_name="gpt-4o-mini")
    agent = Agent.from_open_ai_model(llm=llm)

    llm.add_tool(tool=travaly_tool)
    llm.add_tool(tool=human_assistance_tool)

    llm.bind_tools()

    def chatbot(state: State):
        message = llm.invoke(state["messages"])
        assert len(message.tool_calls) <= 1
        return {"messages": [message]}

    graph_builder = agent.graph_builder

    agent.add_node("chatbot", chatbot)
    # tool_node = BasicToolNode(tools=[travaly_tool])
    tool_node = ToolNode(tools=llm.tools)

    graph_builder.add_node("tools", tool_node)

    # graph_builder.add_conditional_edges(
    #     "chatbot", route_tools, {"tools": "tools", END: END}
    # )
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        # {"tools": "tools", END: END}
    )

    graph_builder.add_edge("tools", "chatbot")
    # graph_builder.set_entry_point("chatbot")
    graph_builder.add_edge(START, "chatbot")

    # graph_builder.add_edge("chatbot", END)

    graph = agent.graph_compile(memory=memory)

    config = {"configurable": {"thread_id": "1"}}

    while True:
        try:
            user_input = input("👤 User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break

            stream_graph_updates(graph, user_input, config)
        except Exception as err:
            loguru.logger.error(err)
            print("[red] ❌ Error en la conversación. [/red]")
            print("[red] ❌ Reiniciando el chatbot. [/red]")
            break


if __name__ == "__main__":
    main()
