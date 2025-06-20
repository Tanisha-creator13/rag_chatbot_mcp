from langchain.embeddings import OpenAIEmbeddings
from pydantic import BaseModel
from supabase import create_client
from django.conf import settings

class KnowledgeBaseTool(BaseModel):
    """Tool to fetch knowledge from Supabase based on semantic similarity."""

    name: str = "Knowledge Base Search Tool"
    description: str = "Fetches documents similar to the user's query using embeddings."

    def _run(self, query: str) -> str:
        try:
            # Initialize OpenAI Embeddings
            embeddings_model = OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY,
                model="text-embedding-3-small"
            )

            # Get embedding for the query
            query_embedding = embeddings_model.embed_query(query)

            # Prepare SQL-compatible embedding string for pgvector
            # vector_str = f"cube(array{str(query_embedding)})"

            # Run the query on Supabase
            response = settings.supabase_client.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_count': 3
                }
            ).execute()

            if response.data:
                docs = [doc['content'] for doc in response.data]
                return "Retrieved Knowledge:\n" + "\n---\n".join(docs)
            else:
                return "No relevant documents found in the knowledge base."

        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return f"An error occurred: {str(e)}"
