from .rag_chain import RAGChain

class MCPServer:
    def __init__(self):
        self.rag = RAGChain()

    def query(self, message: str) -> str:
        return self.rag.generate_answer(message)

