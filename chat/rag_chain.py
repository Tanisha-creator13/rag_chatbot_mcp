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

#     def generate_answer(self, query: str) -> str:
#         try:
#             # If it's a general question , skip Supabase
#             if is_generic_question(query):
#                 return self._call_llm(
#                     prompt=f"Answer briefly and clearly:\n\nQuestion: {query}",
#                     model="gpt-4",
#                     max_tokens=150
#                 )

#             # Else go for Supabase search
#             chunks = self.knowledge_base.retrieve_similar_chunks(query, top_k=3)
#             if not chunks:
#                 return self._call_llm(
#                     prompt=f"Answer using your own knowledge:\n\nQuestion: {query}",
#                     model="gpt-4",
#                     max_tokens=150
#                 )
            
#             # For definition-type questions, give short answers
#             if query.lower().startswith("what is") or query.lower().startswith("define"):
#                 context = "\n\n".join(chunks)[:1500]
#                 prompt = (
#                     f"Use the context below to answer in 1-2 lines:\n\n"
#                     f"{context}\n\nQuestion: {query}"
#                 )
#                 return self._call_llm(prompt, model="gpt-4", max_tokens=100)

#             # For all other RAG cases, use the context
#             summarized_context = self._summarize_chunks(chunks, query)
#             return self._call_llm(
#                 f"Answer using the context:\n{summarized_context}\n\nQuestion: {query}",
#                 model="gpt-4",
#                 max_tokens=300
#             )

#         except Exception as e:
#             return f"Error: {str(e)}"


#     def _summarize_chunks(self, chunks: list[str], query: str) -> str:
#         """Aggressive summarization to stay under 800 tokens"""
#         combined = "\n\n".join(chunks)[:2000] 
        
#         summary_prompt = (
#             "Summarize in 3 bullet points (max 15 words each) "
#             f"relevant to: '{query}':\n\n{combined}\n\nSummary:"
#         )
        
#         summary = self._call_llm(
#             summary_prompt, 
#             model="gpt-3.5-turbo", 
#             max_tokens=150  
#         )
#         return summary
    
#     def _call_llm(self, prompt: str, model: str = "gpt-4", max_tokens: int = 2048) -> str:
#         """Call the LLM with proper parameter handling"""
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


#     def _stream_answer(self, context: str, query: str) -> str:
#         """Stream response to handle long answers"""
#         prompt = (
#             f"Context:\n{context}\n\n"
#             f"Question: {query}\n"
#             "Answer concisely in 3-4 sentences:"
#         )
        
#         # Calculate token usage
#         prompt_tokens = len(self.encoder.encode(prompt))
#         max_answer_tokens = 4096 - prompt_tokens - 10  
        
#         # Get streaming response
#         response = self.client.chat.completions.create(
#             model="gpt-4",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.3,
#             max_tokens=max_answer_tokens,
#             stream=True
#         )
        
#         # Collect streamed response
#         full_answer = []
#         for chunk in response:
#             print("Chunk:", chunk)  # log the entire chunk
#             if chunk.choices[0].delta.content:
#                 full_answer.append(chunk.choices[0].delta.content)

#         print("Final streamed answer:", "".join(full_answer))
#         if not full_answer:
#             return "No answer generated from LLM."

#         return "".join(full_answer)
#         # return "".join(full_answer)
    
from django.conf import settings
from openai import OpenAI
import tiktoken
from .supabase_loader import knowledge_base
from chat.utils.question_classifier import is_generic_question


class RAGChain:
    def __init__(self):
        self.knowledge_base = knowledge_base
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.encoder = tiktoken.encoding_for_model("gpt-4")

    def generate_answer(self, query: str) -> str:
        try:
            if is_generic_question(query):
                return self._call_llm(
                    prompt=f"Answer clearly:\n\nQuestion: {query}",
                    model="gpt-4",
                    max_tokens=150
                )

            chunks = self.knowledge_base.retrieve_similar_chunks(query, top_k=3)

            if not chunks or self._is_context_unrelated(query, chunks):
                return self._call_llm(
                    prompt=f"Answer this clearly using your own knowledge:\n\nQuestion: {query}",
                    model="gpt-4",
                    max_tokens=150
                )

            if query.lower().startswith(("what is", "define")):
                context = "\n\n".join(chunks)[:1500]
                prompt = (
                    f"Use the context below to answer briefly in 1-2 lines:\n\n"
                    f"{context}\n\nQuestion: {query}"
                )
                return self._call_llm(prompt, model="gpt-4", max_tokens=100)

            summarized_context = self._summarize_chunks(chunks, query)
            return self._call_llm(
                f"Answer using the context:\n{summarized_context}\n\nQuestion: {query}",
                model="gpt-4",
                max_tokens=300
            )

        except Exception as e:
            return f"Error: {str(e)}"

    def _summarize_chunks(self, chunks: list[str], query: str) -> str:
        combined = "\n\n".join(chunks)[:2000]
        summary_prompt = (
            f"Summarize the context below in 3 bullet points (max 15 words each), "
            f"relevant to the question: '{query}'\n\n{combined}\n\nSummary:"
        )
        return self._call_llm(summary_prompt, model="gpt-3.5-turbo", max_tokens=150)

    def _call_llm(self, prompt: str, model: str = "gpt-4", max_tokens: int = 2048) -> str:
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

    def _is_context_unrelated(self, query: str, chunks: list[str]) -> bool:
        query_words = set(query.lower().split())
        match_count = 0

        for chunk in chunks:
            chunk_words = set(chunk.lower().split())
            if len(query_words & chunk_words) >= 2:
                match_count += 1

        return match_count == 0
