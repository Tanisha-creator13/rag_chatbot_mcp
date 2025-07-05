# from django.core.management.base import BaseCommand
# from openai import OpenAI
# from supabase import create_client
# import os
# import json

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")  
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# class Command(BaseCommand):
#     help = "Re-generates embeddings for all documents."

#     def handle(self, *args, **kwargs):
#         client = create_client(SUPABASE_URL, SUPABASE_KEY)
#         openai = OpenAI(api_key=OPENAI_API_KEY)

#         print("Fetching documents from Supabase...")
#         docs_response = client.table("documents").select("id", "content").execute()
#         docs = docs_response.data

#         print(f"Found {len(docs)} documents.")
#         for doc in docs:
#             try:
#                 doc_id = int(doc["id"])  # ensure ID is treated as int
#                 content = doc.get("content", "")
#                 if not content or len(content.strip()) < 5:
#                     print(f"Skipping empty/short content for ID {doc_id}")
#                     continue

#                 # Generate embedding
#                 response = openai.embeddings.create(
#                     model="text-embedding-3-small",
#                     input=content
#                 )
#                 embedding = response.data[0].embedding

#                 pg_embedding = f"[{','.join(map(str, embedding))}]"


#                 # Force update using UPSERT
#                 result = client.table("documents").upsert({
#                     "id": doc_id,
#                     "embedding": pg_embedding
#                 }).execute()

#                 print(f"Updated ID {doc_id} → Result: {json.dumps(result.data)}")

#             except Exception as e:
#                 self.stderr.write(f"Error for ID {doc.get('id')}: {e}")


from django.core.management.base import BaseCommand
from openai import OpenAI
from supabase import create_client
import os
import re

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def semantic_chunking_by_paragraph(text, min_length=40):
    """
    Split text into semantic chunks by paragraphs (double newlines).
    Only keep chunks longer than min_length.
    """
    raw_chunks = re.split(r'\n\s*\n', text)
    return [chunk.strip() for chunk in raw_chunks if len(chunk.strip()) > min_length]

class Command(BaseCommand):
    help = "Processes documents into semantic (paragraph-based) chunks with embeddings"

    def handle(self, *args, **options):
        # Initialize clients
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        openai = OpenAI(api_key=OPENAI_API_KEY)
        
        print("Fetching documents from Supabase...")
        docs_response = client.table("documents").select("id", "content").execute()
        docs = docs_response.data
        print(f"Found {len(docs)} documents.")
        
        for doc in docs:
            try:
                doc_id = doc["id"]
                content = doc.get("content", "")
                doc_title = doc.get("title", "")

                if not content or len(content.strip()) < 5:
                    print(f"Skipping empty/short content for ID {doc_id}")
                    continue

                print(f"Processing document: {doc_id}")

                # Semantic chunking by paragraphs
                chunks = semantic_chunking_by_paragraph(content)
                if doc_title:
                    chunks = [f"{doc_title}\n{chunk}" for chunk in chunks]

                print(f"Created {len(chunks)} semantic chunks")

                # Delete existing chunks
                client.table("document_chunks").delete().eq("document_id", doc_id).execute()

                # Process each chunk
                for index, chunk in enumerate(chunks):
                    # Generate embedding for this chunk
                    response = openai.embeddings.create(
                        model="text-embedding-3-small",
                        input=chunk
                    )
                    embedding = response.data[0].embedding

                    # Insert chunk into document_chunks table
                    result = client.table("document_chunks").insert({
                        "document_id": doc_id,
                        "content": chunk,
                        "chunk_index": index,
                        "embedding": embedding
                    }).execute()

                    print(f"Inserted chunk {index} for document {doc_id}")
            
            except Exception as e:
                self.stderr.write(f"Error for ID {doc_id}: {str(e)}")
        
        print("All documents processed successfully!")
