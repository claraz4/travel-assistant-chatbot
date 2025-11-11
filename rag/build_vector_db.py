# Import required modules
import os  # For file and directory operations
import json
from langchain_core.documents import Document

# Import vector database and embedding modules from langchain
from langchain_chroma import Chroma  # Vector database for storing embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings  # Google's embedding model

# Import document loader for PDFs
from langchain_community.document_loaders import PDFPlumberLoader

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google API key for authentication
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the embedding model with Google's embedding model gemini-embedding-exp-03-07
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-exp-03-07",
    google_api_key=api_key
)

# Create/Load a Chroma vector database
vector_store = Chroma(
    collection_name="embeddings",  # Name of the collection to store vectors
    embedding_function=embeddings,  # Function to generate embeddings
    persist_directory="./vector_db2",  # Directory to save the database
    collection_metadata={"hnsw:space": "cosine"}  # Use cosine similarity for vector comparisons
)

# Directory containing PDF files to process
directory_path = os.getenv("DB_FILES_DIRECTORY")

# Loop through all PDF files in the directory
for filename in os.listdir(directory_path):
    # Check if the file is a PDF
    if filename.endswith('.pdf'):
        # Create full file path by joining directory and filename
        file_path = os.path.join(directory_path, filename)

        # Create a PDF loader for the current file
        loader = PDFPlumberLoader(file_path, dedupe=True)

        # Load and parse the PDF into documents
        documents = loader.load()

        # Add the documents to the vector store with their embeddings
        vector_store.add_documents(documents)
    elif filename.endswith(".json"):
        file_path = os.path.join(directory_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # If JSON is a dict → store as one document
        if isinstance(data, dict):
            doc = Document(
                page_content=json.dumps(data),
                metadata={"source": filename}
            )
            vector_store.add_documents([doc])

        # If JSON is a list → store each item separately
        elif isinstance(data, list):
            docs = [
                Document(
                    page_content=json.dumps(item),
                    metadata={"source": filename}
                )
                for item in data
            ]
            vector_store.add_documents(docs)