from .rag_chain import RAGChain

class MCPServer:
    def __init__(self):
        self.context = {}
        self.rag = RAGChain()

    def query(self, message):
        history = self.context.get("history", [])
        history.append({"role": "user", "content": message})

        response = self.rag.generate_answer(message)

        history.append({"role": "assistant", "content": response})
        self.context["history"] = history
        return response

    def query_with_similarity(self, query):
        return self.rag.generate_answer_with_similarity(query)
