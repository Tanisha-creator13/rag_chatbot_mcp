from django.core.management.base import BaseCommand
from openai import OpenAI
from supabase import create_client
import os 

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
class Command(BaseCommand):
    help = "Re-generates embeddings for all documents."

    def handle(self, *args, **kwargs):
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        openai = OpenAI(api_key=OPENAI_API_KEY)

        docs = client.table("documents").select("id", "content").execute().data

        for doc in docs:
            try:
                response = openai.embeddings.create(
                    model="text-embedding-3-small",
                    input=doc["content"]
                )
                embedding = response.data[0].embedding

                client.table("documents").update({
                    "embedding": embedding
                }).eq("id", doc["id"]).execute()

                self.stdout.write(self.style.SUCCESS(f"Updated ID {doc['id']}"))

            except Exception as e:
                self.stderr.write(f"Error for ID {doc['id']}: {e}")
