from django.conf import settings
from openai import OpenAI
from .supabase_loader import knowledge_base
from chat.utils.question_classifier import is_generic_question
import logging
logger = logging.getLogger("rag_chain")

class RAGChain:
    def __init__(self):
        self.knowledge_base = knowledge_base
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.similarity_threshold = 0.6
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
            chunks, similarities = self.knowledge_base.retrieve_similar_chunks(query,top_k=10)
            # Add debug prints
            logger.info(f"Retrieved {len(chunks)} chunks for: '{query}'")
            if chunks:
                logger.info(f"Top similarity: {max(similarities) if similarities else 0}")
                logger.info(f"First chunk: {chunks[0]['content'][:100]}...")
            
            # Filter by similarity threshold
            filtered_chunks = []
            filtered_similarities = []
            for chunk, sim in zip(chunks, similarities):
                if sim >= self.similarity_threshold:
                    filtered_chunks.append(chunk)
                    filtered_similarities.append(sim)

            self.last_retrieved_docs = filtered_chunks

            # Fallback if no relevant chunks
            if not filtered_chunks:
                return self._call_llm(
                    prompt=(
                    "No relevant information was found in the documents. "
                    "If you know the answer from general knowledge, provide it. "
                    "Otherwise, reply: 'Not found in provided documents.'\n\n"
                    f"Question: {query}"
                ),
                    model="gpt-4",
                    max_tokens=100
                )
            context = "\n\n".join([chunk["content"] for chunk in filtered_chunks[:3]])
            prompt = (
            "Using only the information in the context below, answer the question. "
            "If the answer is not in the context, reply: 'Not found in provided documents.'\n\n"
            f"Context:\n{context}\n\nQuestion: {query}"
            )
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
