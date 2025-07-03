# from django.conf import settings
# from openai import OpenAI
# import tiktoken
# from .supabase_loader import knowledge_base
# from chat.utils.question_classifier import is_generic_question

# class RAGChain:
#     def __init__(self):
#         self.knowledge_base = knowledge_base
#         self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
#         self.encoder = tiktoken.encoding_for_model("gpt-4")
#         self.similarity_threshold = 0.4  # Configurable relevance threshold

#     # decides how the query is processed
#     def generate_answer(self, query: str) -> str:
#         try:
#             if is_generic_question(query):
#                 return self._call_llm(
#                     prompt=f"Answer clearly:\n\nQuestion: {query}",
#                     model="gpt-4",
#                     max_tokens=150
#                 )

#             # Retrieve chunks with similarity scores
#             chunks, similarities = self.knowledge_base.retrieve_similar_chunks(query, top_k=3)
            
#             # if content not relevant enough, fallback to using GPT's own gk.
#             if not chunks or self._is_context_unrelated(similarities):
#                 return self._call_llm(
#                     prompt=f"Answer using general knowledge:\n\nQuestion: {query}",
#                     model="gpt-4",
#                     max_tokens=150
#                 )

#             # Definition-style questions
#             if query.lower().startswith(("what is", "define")):
#                 context = "\n\n".join(chunks)[:1200]  # Reduced context
#                 prompt = (
#                     f"Using below context, answer in 1-2 lines:\n\n"
#                     f"{context}\n\nQuestion: {query}"
#                 )
#                 return self._call_llm(prompt, model="gpt-4", max_tokens=100)

#             # Other questions with summarized context
#             summarized_context = self._summarize_chunks(chunks, query)
#             return self._call_llm(
#                 f"Answer using context:\n{summarized_context}\n\nQuestion: {query}",
#                 model="gpt-4",
#                 max_tokens=300
#             )

#         except Exception as e:
#             return f"Error: {str(e)}"

#     # asks GPT-3.5 to summarize the relevant chunks, creates a compressed context before final question
#     def _summarize_chunks(self, chunks: list[str], query: str) -> str:
#         combined = "\n\n".join(chunks)[:1500]  # Reduced input size
#         summary_prompt = (
#             f"Create 3 bullet-point summaries (max 15 words each) "
#             f"relevant to: '{query}'\n\nContext:\n{combined}"
#         )
#         return self._call_llm(summary_prompt, model="gpt-3.5-turbo", max_tokens=150)

#     # Calls GPT using Chat Completion API.
#     def _call_llm(self, prompt: str, model: str, max_tokens: int) -> str:
#         try:
#             response = self.client.chat.completions.create(
#                 model=model,
#                 messages=[
#                     {"role": "system", "content": "You are a helpful assistant."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.3,
#                 max_tokens=max_tokens
#             )
#             return response.choices[0].message.content.strip()
#         except Exception as e:
#             print(f"LLM Error: {str(e)}")
#             return ""

#     def _is_context_unrelated(self, similarities: list[float]) -> bool:
#         """Check if top similarity score meets threshold"""
#         return max(similarities) < self.similarity_threshold if similarities else True


from django.conf import settings
from openai import OpenAI
from .supabase_loader import knowledge_base
from chat.utils.question_classifier import is_generic_question

class RAGChain:
    def __init__(self):
        self.knowledge_base = knowledge_base
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.similarity_threshold = 0.4  # Unified threshold
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
