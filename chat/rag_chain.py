# from langchain.chains import RetrievalQA
# from langchain_openai import OpenAIEmbeddings
from .supabase_loader import knowledge_base
from django.conf import settings
from openai import OpenAI

class RAGChain:
    def __init__(self):
        self.knowledge_base = knowledge_base

    def generate_answer(self, query: str) -> str:
        chunks = self.knowledge_base.retrieve_similar_chunks(query, top_k=1)
        print("Chunks Retrieved:", chunks)

        if not chunks:
            return f"Sorry, I couldn't find relevant information for: {query}"

        context = "\n\n".join(chunks)
        prompt = f"Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"
        print("Prompt being sent to LLM:\n", prompt)

        return self._call_llm(prompt)

    def generate_answer_with_similarity(self, query: str):
        results = self.knowledge_base.retrieve_similar_chunks_with_scores(query, top_k=1)
        if not results:
            return "", 0.0

        top_chunk, similarity = results[0]
        prompt = f"Use the following context to answer the question.\n\nContext:\n{top_chunk}\n\nQuestion: {query}\nAnswer:"
        print("Prompt being sent to LLM:\n", prompt)
        answer = self._call_llm(prompt)
        return answer, similarity

    def _call_llm(self, prompt: str) -> str:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Use only the context provided."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()
