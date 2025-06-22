# from supabase import create_client
# from django.conf import settings
# from openai import OpenAI
# from typing import List
# import json
# import requests

# # Initialize Supabase client
# from django.conf import settings
# supabase_client = settings.SUPABASE_CLIENT

# class SupabaseKnowledgeSource:
#     def __init__(self):
#         self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
#         self.table_name = settings.TABLE_NAME
#         self.text_column = "content"  

#     def retrieve_similar_chunks(self, query: str, top_k: int = 3) -> List[str]:
#         try:
#             embedding = self.client.embeddings.create(
#                 model="text-embedding-3-small",
#                 input=query
#             ).data[0].embedding

#             print(f"Query: {query}")
#             print(f"Embedding: {embedding[:5]}... total: {len(embedding)}")

#             # Use raw HTTP RPC instead of supabase-py
#             raw = self._rpc_match(embedding, top_k)
#             print("Raw RPC JSON:", raw)

#             matches = raw  # <-- FIXED THIS LINE
#             if not matches:
#                 print("No matches found. Full response was:", raw)

#             return [
#                 doc[self.text_column]
#                 for doc in matches
#                 if self._is_valid_chunk(doc.get(self.text_column, ""))
#             ][:top_k]

#         except Exception as e:
#             print(f"Supabase error: {str(e)}")
#             import traceback
#             traceback.print_exc()
#             return []


#     def _rpc_match(self, embedding: List[float], top_k: int = 3):
#         url = f"{settings.SUPABASE_URL}/rest/v1/rpc/match_documents"
#         headers = {
#             "apikey": settings.SUPABASE_KEY,
#             "Authorization": f"Bearer {settings.SUPABASE_KEY}",
#             "Content-Type": "application/json"
#         }
#         payload = {
#             "query_embedding": embedding,
#             "match_count": top_k
#         }
#         resp = requests.post(url, json=payload, headers=headers)
#         try:
#             return resp.json()
#         except Exception:
#             print("RPC error:", resp.status_code, resp.text)
#             return {}

#     def _is_valid_chunk(self, text: str) -> bool:
#         return isinstance(text, str) and len(text.strip()) > 5

# # Initialize knowledge source
# knowledge_base = SupabaseKnowledgeSource()


from supabase import create_client
from django.conf import settings
from openai import OpenAI
from typing import List, Tuple
import requests

supabase_client = settings.SUPABASE_CLIENT

class SupabaseKnowledgeSource:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.table_name = settings.TABLE_NAME
        self.text_column = "content"

    def retrieve_similar_chunks(self, query: str, top_k: int = 3, return_debug=False) -> Tuple[List[str], List[Tuple[int, float]]]:
        try:
            embedding = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            ).data[0].embedding

            print(f"Query: {query}")
            print(f"Embedding: {embedding[:5]}... total: {len(embedding)}")

            raw = self._rpc_match(embedding, top_k)
            debug_info = []

            chunks = []
            for doc in raw:
                sim = doc.get("similarity", 0)
                content = doc.get(self.text_column, "")
                debug_info.append((doc.get("id"), sim))
                if self._is_valid_chunk(content):
                    chunks.append(content)

            return (chunks[:top_k], debug_info) if return_debug else chunks[:top_k]

        except Exception as e:
            print(f"Supabase error: {str(e)}")
            import traceback
            traceback.print_exc()
            return ([], []) if return_debug else []

    def _rpc_match(self, embedding: List[float], top_k: int = 3):
        url = f"{settings.SUPABASE_URL}/rest/v1/rpc/match_documents"
        headers = {
            "apikey": settings.SUPABASE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "query_embedding": embedding,
            "match_count": top_k
        }
        resp = requests.post(url, json=payload, headers=headers)
        try:
            return resp.json()
        except Exception:
            print("RPC error:", resp.status_code, resp.text)
            return []

    def _is_valid_chunk(self, text: str) -> bool:
        return isinstance(text, str) and len(text.strip()) > 5

knowledge_base = SupabaseKnowledgeSource()
