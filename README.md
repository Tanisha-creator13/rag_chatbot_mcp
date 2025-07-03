# RAG Chatbot Project

Hey, Welcome! This project implements a Retrieval-Augmented Generation (RAG) chatbot that combines the power of modern language models with your own document knowledge base.

---
## Backend

- **Django** with REST API endpoints for chat, authentication, and session management
- **Supabase** for user data, authentication, and vector search
- **OpenAI** integration for generating smart, context-aware answers
- **RAG logic** for combining document retrieval with LLM responses

---

## What’s Inside?

- **Document Ingestion & Chunking:** Efficiently processes and embeds documents for fast, relevant retrieval.
- **Smart Retrieval:** Uses vector search (Supabase) to find the most relevant pieces of information for any user query.
- **Conversational AI:** Integrates with OpenAI’s GPT models to generate helpful, context-aware responses.
- **MCP Server Integration:** Supports Model Context Protocol for advanced query handling and future scalability.
- **User Authentication:** Secure endpoints using Supabase JWT.

---

## Frontend

- **Next.js** app for a fast, interactive user experience
- **User authentication** with email and password (Supabase-backed)
- **Clean chat interface** with chat history, session sidebar, and real-time messaging
- **Styled with Tailwind CSS** for a modern, soothing look
- **TypeScript** for type safety and maintainability

---
## Project Structure

- rag_chatbot_clean/
- ├── chat/ # Django backend app
- ├── config/ # Django settings
- ├── manage.py # Django runner
- └── src/ # Next.js frontend (with API routes and UI)

---

## Quick Start

- **Backend:**  
  - Configure Supabase and OpenAI keys  
  - `python manage.py migrate`  
  - `python manage.py runserver`

- **Frontend:**  
  - `cd src`  
  - `npm install`  
  - `npm run dev`

---

**Happy coding! If you have any questions or suggestions, open an issue or join the discussion.**