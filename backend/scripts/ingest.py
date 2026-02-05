
import os
import sys
import time

# Add the project root to sys.path to allow imports from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings

def ingest_data():
    if not settings.PINECONE_API_KEY or not settings.OPENAI_API_KEY:
        print("Error: Please set PINECONE_API_KEY and OPENAI_API_KEY in .env")
        return

    print("Initializing Pinecone...")
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)

    # Delete index if it exists to start fresh (Semantic Chunking replacement)
    try:
        if settings.INDEX_NAME in pc.list_indexes().names():
            print(f"Deleting existing index '{settings.INDEX_NAME}' to re-ingest with Semantic Chunking...")
            pc.delete_index(settings.INDEX_NAME)
            time.sleep(5) # Wait for deletion to propagate
    except Exception as e:
        print(f"Error checking/deleting index: {e}")

    print(f"Creating index '{settings.INDEX_NAME}'...")
    try:
        pc.create_index(
            name=settings.INDEX_NAME,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    except Exception as e:
        print(f"Index creation might have failed (or already exists): {e}")

    print("Loading documents...")
    # Adjust path to data directory
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    documents = SimpleDirectoryReader(data_dir).load_data()
    print(f"Loaded {len(documents)} document pages.")

    print("Setting up Semantic Chunking...")
    embed_model = OpenAIEmbedding(api_key=settings.OPENAI_API_KEY)
    splitter = SemanticSplitterNodeParser(
        buffer_size=1, 
        breakpoint_percentile_threshold=95, 
        embed_model=embed_model
    )

    print("Setting up storage context...")
    vector_store = PineconeVectorStore(pinecone_index=pc.Index(settings.INDEX_NAME))
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
