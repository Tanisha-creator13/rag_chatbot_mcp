from django.conf import settings
from openai import OpenAI
from typing import List, Tuple
import requests
import json

class SupabaseKnowledgeSource:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.table_name = settings.TABLE_NAME
        self.text_column = "content"
        self.embedding_model = "text-embedding-3-small"

    def retrieve_similar_chunks(self, query: str, top_k: int = 3) -> Tuple[List[str], List[float]]:
        try:
            # Generate query embedding
            embedding = self._get_embedding(query)
            
            # Retrieve from Supabase
            raw = self._rpc_match(embedding, top_k)
            
            # Process results
            chunks = []
            similarities = []
            for doc in raw:
                if self._is_valid_chunk(doc.get(self.text_column, "")):
                    chunks.append(doc[self.text_column])
                    similarities.append(doc.get("similarity", 0))
            
            return chunks[:top_k], similarities[:top_k]

        except Exception as e:
            print(f"Supabase error: {str(e)}")
            return [], []

    #Sends a request to OpenAI to turn a string into an embedding vector
    def _get_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {str(e)}")
            return []

    # Calls a PostgreSQL stored function in Supabase named match_documents.
    def _rpc_match(self, embedding: List[float], top_k: int):
        url = f"{settings.SUPABASE_URL}/rest/v1/rpc/match_chunks"
        headers = {
            "apikey": settings.SUPABASE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        # payload = {"query_embedding": embedding, "match_count": top_k}
        payload = {"query_embedding": embedding, "match_count": top_k, "similarity_threshold":0.4}
        
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"RPC error: {str(e)}")
            return []

    def _is_valid_chunk(self, text: str) -> bool:
        return bool(text) and len(text.strip()) > 10

# Singleton instance
knowledge_base = SupabaseKnowledgeSource()
