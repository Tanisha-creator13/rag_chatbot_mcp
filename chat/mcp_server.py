# from .rag_chain import RAGChain

# class MCPServer:
#     def __init__(self):
#         self.rag = RAGChain()

#     def query(self, message: str) -> str:
#         return self.rag.generate_answer(message)

import threading
from django.conf import settings
from .rag_chain import RAGChain

class MCPServer:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.rag = RAGChain()
        return cls._instance

    def query(self, message: str) -> dict:
        try:
            # Add caching layer here if needed
            response = self.rag.generate_answer(message)
            
            # Get context sources from RAG if available
            context_sources = getattr(self.rag, 'last_retrieved_docs', [])
            
            return {
                "response": response,
                "context": [doc['id'] for doc in context_sources][:3],
                "model": settings.LLM_MODEL  # From settings.py
            }
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "context": []
            }
