from langchain_openai import ChatOpenAI
from core.llm.base import BaseLLMService

class OpenAIService(BaseLLMService):
    """OpenAI specific implementation"""
    
    def __init__(self, model_name: str, **kwargs):
        super().__init__()
        self._model = ChatOpenAI(model=model_name, **kwargs)
    
    def invoke(self, prompt):
        if not self._model:
            raise ValueError("Model not initialized")
        return self._model.invoke(prompt)
    
    def bind_tools(self):
        if not self._tools:
            raise ValueError("No tools registered")
        self._model = self._model.bind_tools(self._tools)
    
    def add_tool(self, tool):
        self._tools.append(tool)