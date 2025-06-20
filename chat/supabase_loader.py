from supabase import create_client
from django.conf import settings
from openai import OpenAI
from typing import List

# Initialize Supabase client
from django.conf import settings
supabase_client = settings.SUPABASE_CLIENT

class SupabaseKnowledgeSource:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.table_name = settings.TABLE_NAME
        self.text_column = "content"  

    def retrieve_similar_chunks(self, query: str, top_k: int = 3) -> List[str]:
        try:
            embedding = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            ).data[0].embedding

            print(f"Query: {query}")
            print(f"Embedding: {embedding[:5]}... total: {len(embedding)}")

            # Correct RPC call
            embedding_str = f"[{','.join(map(str, embedding))}]"

            response = supabase_client.rpc(
                "match_documents",
                {
                    "query_embedding": embedding_str,
                    "match_count": top_k
                }
            ).execute()

            print("Raw Supabase response:", response.data)

            return [
                doc[self.text_column]
                for doc in response.data
                if self._is_valid_chunk(doc.get(self.text_column, ""))
            ][:top_k]

        except Exception as e:
            print(f"Supabase error: {str(e)}")
            import traceback
            traceback.print_exc()
            return []


    def _is_valid_chunk(self, text: str) -> bool:
        return isinstance(text, str) and len(text.strip()) > 5

# Initialize knowledge source
knowledge_base = SupabaseKnowledgeSource()
