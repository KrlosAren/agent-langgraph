from typing import Dict, Any
from datetime import datetime
from langgraph.checkpoint.memory import MemorySaver

class EnhancedMemorySaver(MemorySaver):
    """Memoria mejorada usando el checkpointer de langgraph"""

    def __init__(self, max_messages: int = 100):
        super().__init__()
        self.max_messages = max_messages

    def get_memory_key(self, config: Dict[str, Any]) -> str:
        """Obtiene la clave de memoria basada en la configuración"""
        return config.get("configurable", {}).get("thread_id", "default")

    async def load(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Carga el estado de la memoria"""
        memory_key = self.get_memory_key(config)

        try:
            # Intentar cargar la memoria existente
            stored_data = await super().storage.get(memory_key)
            if stored_data:
                return stored_data
        except Exception:
            # Si no hay memoria previa, inicializar una nueva
            return {
                "messages": [],
                "metadata": {
                    "session_start": datetime.now().isoformat(),
                    "memory_key": memory_key,
                    "message_count": 0,
                },
            }
        return stored_data

    async def save(self, config: Dict[str, Any], state: Dict[str, Any]) -> None:
        """Guarda el estado actual en memoria"""
        # Actualizar metadatos
        if "metadata" not in state:
            state["metadata"] = {}

        state["metadata"]["last_updated"] = datetime.now().isoformat()
        state["metadata"]["message_count"] = len(state.get("messages", []))

        # Limitar el número de mensajes almacenados
        if len(state.get("messages", [])) > self.max_messages:
            state["messages"] = state["messages"][-self.max_messages :]

        await super().save(config, state)
