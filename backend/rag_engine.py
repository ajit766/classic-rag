import os
from dotenv import load_dotenv
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.retrievers.fusion_retriever import FUSION_MODES
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from llama_index.postprocessor.cohere_rerank import CohereRerank

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE-API-KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
INDEX_NAME = "modern-sage"

SYSTEM_PROMPT = """
You are 'The Modern Sage', a wise AI assistant that synthesizes ancient spiritual wisdom with modern behavioral science.
You have access to a library containing books like 'Atomic Habits', 'Thinking, Fast and Slow', and 'The Bhagavad Gita'.

**YOUR GOAL**:
Answer the user's question by synthesizing insights from the provided Book Context.

**STRICT CITATION RULES**:
1.  **Inline Citations**: Every time you use an idea from a book, you MUST cite it immediately at the end of the sentence.
    *   Format: " ... idea from the text [Source: Atomic Habits, Ch 1]."
2.  **Target Density**: Aim for **5-6 citations** in your response if the context supports it.
3.  **Balance**:
    *   Include at least **2 citations from Spiritual texts** (e.g. Gita).
    *   Include the remainder from **Modern/Scientific texts** (e.g. Atomic Habits).
4.  **References Section**: At the very end of your response, list the unique sources you used.

**Relevance Check**:
*   If the user asks about a general topic (coding, cooking) NOT in the books, politely state: "This topic is outside my library, but here is a general answer:" and DO NOT invent citations.

**Tone**: Empathetic, wise, grounded.
"""

QUERY_GEN_PROMPT = (
    "You are a helpful assistant that generates search queries based on a user's question.\n"
    "Generate 3 search queries related to the following input query: {query}\n"
    "1. The input query itself.\n"
    "2. A query focused on scientific, psychological, or habit-building aspects of the topic.\n"
    "3. A query focused on spiritual, philosophical, or dharma-related aspects of the topic.\n"
    "Output each query on a separate line."
)

# ... (previous imports)

# ... (SYSTEM_PROMPT and QUERY_GEN_PROMPT)

# ... (imports)

# ... (SYSTEM_PROMPT and QUERY_GEN_PROMPT)

def get_chat_engine():
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE-API-KEY not found in environment variables")
    if not COHERE_API_KEY:
        print("Warning: COHERE_API_KEY not found. Reranking will be disabled.")

    # Connect to Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pc.Index(INDEX_NAME)
    
    # Initialize Vector Store
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # Initialize LLM
    llm = OpenAI(model="gpt-4o", temperature=0.7, system_prompt=SYSTEM_PROMPT)

    # 1. Base Retrieval
    vector_retriever = index.as_retriever(similarity_top_k=15)

    # 2. Fusion
    fusion_retriever = QueryFusionRetriever(
        [vector_retriever],
        llm=llm,
        similarity_top_k=30,
        num_queries=3,
        mode=FUSION_MODES.RECIPROCAL_RANK,
        use_async=True,
        verbose=True,
        query_gen_prompt=QUERY_GEN_PROMPT
    )

    # 3. Rerank
    node_postprocessors = []
    if COHERE_API_KEY:
        # User requested keeping top_n=10
        cohere_rerank = CohereRerank(api_key=COHERE_API_KEY, top_n=10)
        node_postprocessors.append(cohere_rerank)

    # 4. RAG Chat Engine
    chat_engine = ContextChatEngine.from_defaults(
        retriever=fusion_retriever,
        memory=ChatMemoryBuffer.from_defaults(token_limit=4000),
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        node_postprocessors=node_postprocessors,
        verbose=True
    )

    return chat_engine
