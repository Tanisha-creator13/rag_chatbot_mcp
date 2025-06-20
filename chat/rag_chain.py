from django.conf import settings
from openai import OpenAI
import tiktoken  
from .supabase_loader import knowledge_base

class RAGChain:
    def __init__(self):
        self.knowledge_base = knowledge_base
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.encoder = tiktoken.encoding_for_model("gpt-4")

    def generate_answer(self, query: str) -> str:
        try:
            chunks = self.knowledge_base.retrieve_similar_chunks(query, top_k=3)
            if not chunks:
                return "I couldn't find relevant information."
            
            summarized_context = self._summarize_chunks(chunks, query)
            
            return self._stream_answer(summarized_context, query)
            
        except Exception as e:
            return f"Error: {str(e)}"

    def _summarize_chunks(self, chunks: list[str], query: str) -> str:
        """Aggressive summarization to stay under 800 tokens"""
        combined = "\n\n".join(chunks)[:2000] 
        
        summary_prompt = (
            "Summarize in 3 bullet points (max 15 words each) "
            f"relevant to: '{query}':\n\n{combined}\n\nSummary:"
        )
        
        summary = self._call_llm(
            summary_prompt, 
            model="gpt-3.5-turbo", 
            max_tokens=150  
        )
        return summary
    
    def _call_llm(self, prompt: str, model: str = "gpt-4", max_tokens: int = 2048) -> str:
        """Call the LLM with proper parameter handling"""
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


    def _stream_answer(self, context: str, query: str) -> str:
        """Stream response to handle long answers"""
        prompt = (
            f"Context:\n{context}\n\n"
            f"Question: {query}\n"
            "Answer concisely in 3-4 sentences:"
        )
        
        # Calculate token usage
        prompt_tokens = len(self.encoder.encode(prompt))
        max_answer_tokens = 4096 - prompt_tokens - 10  
        
        # Get streaming response
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=max_answer_tokens,
            stream=True
        )
        
        # Collect streamed response
        full_answer = []
        # for chunk in response:
        #     if chunk.choices[0].delta.content:
        #         full_answer.append(chunk.choices[0].delta.content)
        
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                full_answer.append(delta.content)

        return "".join(full_answer)
    

