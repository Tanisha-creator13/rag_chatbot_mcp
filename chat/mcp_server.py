from .rag_chain import RAGChain

class MCPServer:
    def __init__(self):
        self.context = {}
        self.rag = RAGChain()

    def query(self, message):
        history = self.context.get("history", [])
        history.append({"role": "user", "content": message})
        response = self.rag.run(message)
        history.append({"role": "assistant", "content": response})
        self.context["history"] = history
        return response
