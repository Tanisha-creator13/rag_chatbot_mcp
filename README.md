# MCP RAG Chatbot (Django Backend)

A lightweight backend chatbot built with **Django**, integrating **MCPServer**, **Retrieval-Augmented Generation (RAG)**, **FAISS** for semantic search, and **OpenAI** for response generation.

---

## Features

- **MCPServer Integration**: Maintains conversational context with memory.
- **Basic RAG Setup**: Retrieves relevant chunks before generating response.
- **FAISS Embeddings**: Uses in-memory FAISS index for similarity search.

---
## Why This is Pretty Cool

Imagine if your chatbot wasn’t just a goldfish (forgetting everything every time you say something new)...

With **MCP RAG Chatbot**, you're giving your bot a **brain with memory** — one that remembers what you said, understands what you mean, and digs deeper to give you better answers.

## Stack

- **Backend**: Django, Django REST Framework  
- **Semantic Search**: FAISS (in-memory)  
- **LLM**: OpenAI GPT (via API)  
- **MCP**: Custom `MCPServer` to manage context  

---

## Running Locally
### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/mcp-rag-chatbot.git
cd mcp-rag-chatbot
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```
## API Usage 
POST /chat/ -> send a query to the chatbot
