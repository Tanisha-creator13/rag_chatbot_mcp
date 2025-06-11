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
