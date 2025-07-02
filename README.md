# RAG Chatbot Project

Hey, Welcome! This project implements a Retrieval-Augmented Generation (RAG) chatbot that combines the power of modern language models with your own document knowledge base.

---

## What’s Inside?

- **Document Ingestion & Chunking:** Efficiently processes and embeds documents for fast, relevant retrieval.
- **Smart Retrieval:** Uses vector search (Supabase) to find the most relevant pieces of information for any user query.
- **Conversational AI:** Integrates with OpenAI’s GPT models to generate helpful, context-aware responses.
- **MCP Server Integration:** Supports Model Context Protocol for advanced query handling and future scalability.
- **User Authentication:** Secure endpoints using Supabase JWT.
- **Ready for Frontend:** API endpoints are designed to work seamlessly with any frontend.

---

## Directory Highlights


---

## Getting Started

1. **Install dependencies**  
- pip install -r requirements.txt
2. **Set up your environment variables**  
- Supabase URL and key
- OpenAI API key
3. **Run database migrations**  
- python manage.py migrate
4. **Process your documents** 
- python manage.py reembed_documents
5. **Start the development server**  
- python manage.py runserver

**Happy coding! If you have any questions or suggestions, open an issue or join the discussion.**