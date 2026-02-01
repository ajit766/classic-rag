import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE-API-KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "modern-sage"

def ingest_data():
    if not PINECONE_API_KEY or not OPENAI_API_KEY:
        print("Error: Please set PINECONE_API_KEY and OPENAI_API_KEY in .env")
        return

    print("Initializing Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Create index if it doesn't exist
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating index '{INDEX_NAME}'...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536, # OpenAI text-embedding-3-small dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    else:
        print(f"Index '{INDEX_NAME}' already exists.")

    print("Loading documents...")
    # Load documents from data/ directory
    documents = SimpleDirectoryReader("./data").load_data()
    print(f"Loaded {len(documents)} document pages.")

    print("Setting up storage context...")
    vector_store = PineconeVectorStore(pinecone_index=pc.Index(INDEX_NAME))
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Indexing documents (this might take a while)...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    
    print("Success! Documents indexed.")

if __name__ == "__main__":
    ingest_data()
