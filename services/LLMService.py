class LLMService:

    def __init__(self, model):
        self._model = model
        self._tools = []

    @classmethod
    def from_openai(cls, model_name):
        from langchain_openai import ChatOpenAI
        return cls(ChatOpenAI(model=model_name))
    
    @property
    def model(self):
        return self._model

    @property
    def tools(self):
        if not self._tools:
            print("⚠️ No hay herramientas registradas en el modelo.")
            raise Exception("No hay herramientas registradas en el modelo.")
        return self._tools

    def add_tool(self, tool):
        self._tools.append(tool)

    def bind_tools(self):
        """Asocia las herramientas al modelo y actualiza self._model"""
        if not self._tools:
            print("⚠️ No hay herramientas registradas en el modelo.")
            raise Exception("No hay herramientas registradas en el modelo.")
        self._model = self._model.bind_tools(self._tools)

    def invoke(self, prompt):
        return self._model.invoke(prompt)
