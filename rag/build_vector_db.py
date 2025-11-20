
# Import required modules
import os
import json

# rag/build_vector_db.py

import os
import json
from pathlib import Path

from dotenv import load_dotenv
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


# ----- Paths & env loading -----

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PERSIST_DIR = str(PROJECT_ROOT / "vector_db2")

# Load .env from the project root
load_dotenv()


# ----- API key setup -----

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set. Please add it to your .env file.")

# Force Google client libraries to use this key
os.environ["GOOGLE_API_KEY"] = api_key
os.environ["GOOGLE_GENERATIVE_AI_API_KEY"] = api_key  # some tools look for this name

# ----- Embeddings & vector store -----

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-exp-03-07",
    # key picked up from env var above
)


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

# ----- Load files (PDF + JSON) and add to DB -----

# Example: DB_FILES_DIRECTORY=json  OR  ./pdfs,./json
dirs_env = os.getenv("DB_FILES_DIRECTORY", "./pdfs,./json")
dirs = [d.strip() for d in dirs_env.split(",") if d.strip()]

if not dirs:
    print("No input directories specified in DB_FILES_DIRECTORY; nothing to index.")
else:
    for directory_path in dirs:
        # make relative paths start from project root
        if not os.path.isabs(directory_path):
            directory_path = str((PROJECT_ROOT / directory_path).resolve())

        if not os.path.exists(directory_path):
            print(f"⚠️  Skipping missing folder: {directory_path}")
            continue

        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)

            # ----- PDFs -----
            if filename.lower().endswith(".pdf"):
                loader = PDFPlumberLoader(file_path, dedupe=True)
                documents = loader.load()
                vector_store.add_documents(documents)
                print(f"✅ Added PDF: {filename}")

            # ----- JSON -----
            elif filename.lower().endswith(".json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"⚠️  Skipping invalid JSON file {filename}: {e}")
                    continue

                docs_to_add: list[Document] = []

                if isinstance(data, dict):
                    docs_to_add.append(
                        Document(
                            page_content=json.dumps(data, ensure_ascii=False),
                            metadata={"source": filename},
                        )
                    )
                elif isinstance(data, list):
                    for item in data:
                        docs_to_add.append(
                            Document(
                                page_content=json.dumps(item, ensure_ascii=False),
                                metadata={"source": filename},
                            )
                        )
                else:
                    # Fallback: store whatever it is as a single string
                    docs_to_add.append(
                        Document(
                            page_content=json.dumps(data, ensure_ascii=False),
                            metadata={"source": filename},
                        )
                    )

                if docs_to_add:
                    vector_store.add_documents(docs_to_add)
                print(f"✅ Added JSON: {filename}")

# ----- Persist DB -----

#vector_store.persist()
print(f"🎉 Vector database built and saved to: {PERSIST_DIR}")

