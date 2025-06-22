from django.core.management.base import BaseCommand
from openai import OpenAI
from supabase import create_client
import os
import json

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class Command(BaseCommand):
    help = "Re-generates embeddings for all documents."

    def handle(self, *args, **kwargs):
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        openai = OpenAI(api_key=OPENAI_API_KEY)

        print("Fetching documents from Supabase...")
        docs_response = client.table("documents").select("id", "content").execute()
        docs = docs_response.data

        print(f"Found {len(docs)} documents.")
        for doc in docs:
            try:
                doc_id = int(doc["id"])  # ensure ID is treated as int
                content = doc.get("content", "")
                if not content or len(content.strip()) < 5:
                    print(f"Skipping empty/short content for ID {doc_id}")
                    continue

                # Generate embedding
                response = openai.embeddings.create(
                    model="text-embedding-3-small",
                    input=content
                )
                embedding = response.data[0].embedding

                pg_embedding = f"[{','.join(map(str, embedding))}]"


                # Force update using UPSERT
                result = client.table("documents").upsert({
                    "id": doc_id,
                    "embedding": pg_embedding
                }).execute()

                print(f"Updated ID {doc_id} → Result: {json.dumps(result.data)}")

            except Exception as e:
                self.stderr.write(f"Error for ID {doc.get('id')}: {e}")
