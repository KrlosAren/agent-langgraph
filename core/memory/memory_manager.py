from typing import Dict, Any, List, Optional
from datetime import datetime

from core.memory.base import MessageMemory

from core.memory.langgraph_memory import EnhancedMemorySaver


class MemoryManager:
    """Gestor de memoria para el agente"""

    def __init__(self, memory_saver: EnhancedMemorySaver):
        self.memory_saver = memory_saver

    async def get_context(
        self, config: Dict[str, Any], query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Obtiene contexto relevante de la memoria"""
        state = await self.memory_saver.load(config)
        messages = state.get("messages", [])

        if not messages:
            return []

        # Aquí podrías implementar búsqueda semántica más sofisticada
        # Por ahora, simplemente devolvemos los últimos mensajes relevantes
        return messages[-limit:]

    async def add_to_memory(
        self,
        config: Dict[str, Any],
        message: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Añade un nuevo mensaje a la memoria"""
        state = await self.memory_saver.load(config)

        message_memory = MessageMemory(
            content=message["content"],
            role=message["role"],
            timestamp=datetime.now(),
            metadata=metadata or {},
        )

        if "messages" not in state:
            state["messages"] = []

        state["messages"].append(message_memory.dict())
        await self.memory_saver.save(config, state)
