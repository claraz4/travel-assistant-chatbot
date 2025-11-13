# Import required modules
import os
import json
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader
from dotenv import load_dotenv
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PERSIST_DIR = str(PROJECT_ROOT / "vector_db2")


# Load environment variables
load_dotenv()

# Google API key
api_key = os.getenv("GEMINI_API_KEY")

# Initialize Gemini embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-exp-03-07",
    google_api_key=api_key
)

# Create or load Chroma vector database
vector_store = Chroma(
    collection_name="embeddings",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
    collection_metadata={"hnsw:space": "cosine"},
)


# Get both directories 
dirs = os.getenv("DB_FILES_DIRECTORY", "./pdfs,./json").split(",")

# Loop through each directory
for directory_path in [d.strip() for d in dirs if d.strip()]:
    if not os.path.exists(directory_path):
        print(f"Skipping missing folder: {directory_path}")
        continue

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        if filename.endswith(".pdf"):
            loader = PDFPlumberLoader(file_path, dedupe=True)
            documents = loader.load()
            vector_store.add_documents(documents)
            print(f"✅ Added PDF: {filename}")

        elif filename.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                doc = Document(page_content=json.dumps(data), metadata={"source": filename})
                vector_store.add_documents([doc])
            elif isinstance(data, list):
                docs = [Document(page_content=json.dumps(i), metadata={"source": filename}) for i in data]
                vector_store.add_documents(docs)
            print(f"✅ Added JSON: {filename}")
