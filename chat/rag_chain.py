from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
# os.environ["OPENAI_API_KEY"] = "your-key"
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

class RAGChain:
    def __init__(self):
        loader = TextLoader("chat/data.txt")  
        docs = loader.load()
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(docs, embeddings)
        retriever = vectorstore.as_retriever()
        self.qa = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(), retriever=retriever, return_source_documents=False
        )

    def run(self, query):
        return self.qa.run(query)
