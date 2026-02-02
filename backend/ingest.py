import os
import time
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE-API-KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "modern-sage"

def ingest_data():
    if not PINECONE_API_KEY or not OPENAI_API_KEY:
        print("Error: Please set PINECONE-API-KEY and OPENAI_API_KEY in .env")
        return

    print("Initializing Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Delete index if it exists to start fresh (Semantic Chunking replacement)
    if INDEX_NAME in pc.list_indexes().names():
        print(f"Deleting existing index '{INDEX_NAME}' to re-ingest with Semantic Chunking...")
        pc.delete_index(INDEX_NAME)
        time.sleep(5) # Wait for deletion to propagate

    print(f"Creating index '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

    print("Loading documents...")
    documents = SimpleDirectoryReader("./data").load_data()
    print(f"Loaded {len(documents)} document pages.")

    print("Setting up Semantic Chunking...")
    embed_model = OpenAIEmbedding()
    splitter = SemanticSplitterNodeParser(
        buffer_size=1, 
        breakpoint_percentile_threshold=95, 
        embed_model=embed_model
    )

    print("Setting up storage context...")
    vector_store = PineconeVectorStore(pinecone_index=pc.Index(INDEX_NAME))
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Indexing documents with Semantic Splitting (this will take longer due to embedding calculation)...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=[splitter]
    )
    
    print("Success! Documents indexed with Semantic Chunking.")

if __name__ == "__main__":
    ingest_data()
