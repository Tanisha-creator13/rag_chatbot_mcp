# from typing import Dict, Any, List
# from supabase import create_client
# from django.conf import settings
# from openai import OpenAI
# import unicodedata

# # Initialize Supabase client
# supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# def is_valid_text(text: str) -> bool:
#     """Check if text is non-empty, within length range, and not control-character heavy."""
#     if not isinstance(text, str) or not (100 < len(text) < 5000):
#         return False
#     if '\x00' in text:
#         return False
#     try:
#         sample = text[:300]
#         if any(unicodedata.category(c)[0] == "C" for c in sample):
#             return False
#     except Exception:
#         return False
#     return True

# class SupabaseKnowledgeSource:
#     def __init__(self, supabase_client, table_name: str, limit: int = 5, text_column: str = "content"):
#         self.supabase_client = supabase_client
#         self.table_name = table_name
#         self.limit = limit
#         self.text_column = text_column
#         self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

#     def load_content(self) -> Dict[Any, str]:
#         """Fetch and return valid content from Supabase."""
#         try:
#             response = self.supabase_client.table(self.table_name).select("*").limit(50).execute()
#             if not response.data:
#                 raise ValueError("No data returned from Supabase.")
#             formatted_data = self.validate_content(response.data)
#             return {self.table_name: formatted_data}
#         except Exception as e:
#             raise ValueError(f"Failed to fetch data from Supabase: {e}")

#     def validate_content(self, records: List[Dict[str, Any]]) -> str:
#         """Format valid entries into a single string."""
#         formatted = f"Data from Supabase table '{self.table_name}':\n\n"
#         valid_count = 0

#         for record in records:
#             text = record.get(self.text_column, "")
#             if is_valid_text(text):
#                 formatted += f"- {text}\n"
#                 valid_count += 1
#             if valid_count >= self.limit:
#                 break

#         return formatted

#     def retrieve_similar_chunks(self, query: str, top_k: int = 3) -> List[str]:
#         """Find similar chunks to the query using Supabase vector search."""
#         client = OpenAI(api_key=settings.OPENAI_API_KEY)

#         try:
#             embedding_response = client.embeddings.create(
#                 model="text-embedding-3-small",
#                 input=query
#             )
#             query_embedding = embedding_response.data[0].embedding
#             query_vector_str = f"[{','.join(map(str, query_embedding))}]"

#             rpc_response = self.supabase_client.rpc("match_documents", {
#                 "query_embedding": query_vector_str,
#                 "match_count": top_k * 100
#             }).execute()

#             chunks = []
#             for doc in rpc_response.data:
#                 text = doc.get(self.text_column, "")
#                 if is_valid_text(text):
#                     chunks.append(text)
#                     if len(chunks) == top_k:
#                         break

#             return chunks

#         except Exception as e:
#             print(f"Error retrieving chunks: {e}")
#             return []
    
#     def retrieve_similar_chunks_with_scores(self, query: str, top_k: int = 1):
#         embedding = self.embed_query(query)
#         response = self.supabase_client.rpc('match_documents', {
#             'query_embedding': embedding,\
#             'match_count': top_k
#         }).execute()

#         if not response.data:
#             return []

#         return [(item['content'], item.get('similarity', 0.0)) for item in response.data]
    
#     def embed_query(self, query: str) -> List[float]:
#         embedding_response = self.client.embeddings.create(
#             model="text-embedding-3-small",
#             input=query
#         )
#         return embedding_response.data[0].embedding


# # Initialize the knowledge source
# knowledge_base = SupabaseKnowledgeSource(
#     supabase_client=supabase_client,
#     table_name=settings.TABLE_NAME,
#     limit=5,
#     text_column="content"
# )

from supabase import create_client
from django.conf import settings
from openai import OpenAI
from typing import List

# Initialize Supabase client
supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

class SupabaseKnowledgeSource:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.table_name = settings.TABLE_NAME
        self.text_column = "content"  

    def retrieve_similar_chunks(self, query: str, top_k: int = 3) -> List[str]:
        """Get relevant chunks from Supabase using vector search"""
        try:
            # Generate embedding
            embedding = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            ).data[0].embedding

            # Query Supabase
            response = supabase_client.rpc(
                'match_documents',
                {
                    'query_embedding': embedding,
                    'match_count': top_k
                }
            ).execute()

            # Extract valid chunks
            return [
                doc[self.text_column] 
                for doc in response.data
                if self._is_valid_chunk(doc.get(self.text_column, ""))
            ][:top_k]

        except Exception as e:
            print(f"Supabase error: {str(e)}")
            return []

    def _is_valid_chunk(self, text: str) -> bool:
        """Simplified validation"""
        return isinstance(text, str) and 10 < len(text) < 10000

# Initialize knowledge source
knowledge_base = SupabaseKnowledgeSource()
