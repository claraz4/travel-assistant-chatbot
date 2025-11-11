from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

@tool
def search_vector_db(query: str) -> str:
    """Search the vector database for relevant documents."""
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-exp-03-07",
        google_api_key=api_key
    )

    vector_store = Chroma(
        collection_name="embeddings",
        embedding_function=embeddings,
        persist_directory="./vector_db2",
        collection_metadata={"hnsw:space": "cosine"}
    )

    result = vector_store.similarity_search(query=query, k=5)
    return "\n".join([doc.page_content for doc in result])
