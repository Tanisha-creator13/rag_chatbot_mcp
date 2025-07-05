from django.conf import settings
from openai import OpenAI
from .supabase_loader import knowledge_base
from chat.utils.question_classifier import is_generic_question

class RAGChain:
    def __init__(self):
        self.knowledge_base = knowledge_base
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.similarity_threshold = 0.4  
        self.last_retrieved_docs = []

    def generate_answer(self, query: str) -> str:
        try:
            if is_generic_question(query):
                return self._call_llm(
                    prompt=f"Answer clearly:\n\nQuestion: {query}",
                    model="gpt-4",
                    max_tokens=150
                )

            # Retrieve chunks with similarity scores
            chunks, similarities = self.knowledge_base.retrieve_similar_chunks(query)
            # Add debug prints
            print(f"Retrieved {len(chunks)} chunks for: '{query}'")
            if chunks:
                print(f"Top similarity: {max(similarities) if similarities else 0}")
                print(f"First chunk: {chunks[0]['content'][:100]}...")
            
            self.last_retrieved_docs = chunks

            # Fallback if no relevant chunks
            if not chunks or max(similarities) < self.similarity_threshold:
                return self._call_llm(
                    prompt=f"Answer using general knowledge:\n\nQuestion: {query}",
                    model="gpt-4",
                    max_tokens=300
                )
            
            # Handle definition-style questions differently
            if query.lower().startswith(("what is", "define")):
                context = "\n\n".join([chunk["content"] for chunk in chunks])[:1200]
                prompt = (
                    f"Define concisely using context:\n{context}\n\nQuestion: {query}"
                )
                return self._call_llm(prompt, model="gpt-4", max_tokens=100)
            
            # Standard context handling
            context = "\n\n".join([chunk["content"] for chunk in chunks[:3]])
            prompt = f"Answer using context:\n{context}\n\nQuestion: {query}"
            return self._call_llm(prompt, model="gpt-4", max_tokens=300)

        except Exception as e:
            return f"Error: {str(e)}"

    def _call_llm(self, prompt: str, model: str, max_tokens: int) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM Error: {str(e)}")
            return ""
