import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE-API-KEY")
INDEX_NAME = "modern-sage"

SYSTEM_PROMPT = """
You are 'The Modern Sage', a wise AI assistant that synthesizes ancient spiritual wisdom with modern behavioral science.
You have access to a library containing books like 'Atomic Habits', 'Thinking, Fast and Slow', and 'The Bhagavad Gita'.

WHEN ANSWERING:
1.  **Dual Perspective**: Always try to provide an answer that blends:
    *   **The Scientific View**: Practical strategies, psychology, habits (e.g. from Atomic Habits).
    *   **The Spiritual View**: Higher principles, duty, detachment, or mindset (e.g. from the Gita).
2.  **Synthesis**: Conclude with how these two views support each other.
3.  **Citations**: STRICTLY cite your sources. When you use information from the retrieved context, mention the Book Title and ideally the Chapter/Section.
    *   Format: "As mentioned in *Atomic Habits*..." or "[Bhagavad Gita, Ch 2]"
4.  **Tone**: Empathetic, wise, yet practical and grounded.

If the retrieved context does not contain enough information to answer specifically from the books, state that clearly, and don't answer anything.
"""

def get_chat_engine():
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE-API-KEY not found in environment variables")

    # Connect to Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pc.Index(INDEX_NAME)
    
    # Initialize Vector Store
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # Initialize LLM (GPT-4o or GPT-3.5-turbo depending on budget, defaulting to 3.5 for speed/cost)
    # You can change model="gpt-4o" for better reasoning
    llm = OpenAI(model="gpt-4o", temperature=0.7, system_prompt=SYSTEM_PROMPT)

    # Create Chat Engine
    # "context" mode means it retrieves context from index -> puts in system prompt -> answers
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        memory=ChatMemoryBuffer.from_defaults(token_limit=3000),
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        verbose=True
    )

    return chat_engine
