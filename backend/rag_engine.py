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
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore
from typing import List, Optional

load_dotenv()

from llama_index.core import set_global_handler

# Initialize Observability (Langfuse)
if os.getenv("LANGFUSE_SECRET_KEY"):
    try:
        set_global_handler("langfuse", 
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST")
        )
        print("--- Langfuse Observability Enabled (Callback Mode) ---")
    except ImportError:
        print("Warning: 'llama-index-callbacks-langfuse' not installed.")
    except Exception as e:
        print(f"Warning: Failed to init Langfuse: {e}")

PINECONE_API_KEY = os.getenv("PINECONE-API-KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
INDEX_NAME = "modern-sage"

SYSTEM_PROMPT = """
You are 'The Modern Sage', a wise AI assistant that synthesizes ancient spiritual wisdom with modern behavioral science.
You have access to a library containing books like 'Atomic Habits', 'Thinking, Fast and Slow', and 'The Bhagavad Gita'.

**YOUR GOAL**:
Answer the user's question by synthesizing insights from the provided Book Context.

**STRUCTURED RESPONSE FORMAT**:
You must structure your answer into two distinct sections:

### 1. The Spiritual Perspective (Ancient Wisdom)
*   **Focus**: Answer based **ONLY** on the *Bhagavad Gita*.
*   **Requirement**: You must include **2-3 citations** from the Gita.
*   **Tone**: Profound, timeless, dharma-focused.

### 2. The Scientific Perspective (Modern Strategy)
*   **Focus**: Answer based on modern psychology/habit books (e.g., *Atomic Habits*, *Thinking Fast & Slow*,*Ikigai*, *The 7 habits of highly effective people).
*   **Requirement**: You must include **3-4 citations** from these modern texts.
*   **Tone**: Actionable, tactical, evidence-based.

**STRICT CITATION RULES**:
1.  **Inline Citations**: Every time you use an idea, cite it immediately at the end of the sentence.
    *   Format: " ... idea from the text [Source: Atomic Habits, Ch 1]."
2.  **References Section**: At the very end, list the unique sources used.

**Relevance Check**:
*   If the user asks about a general topic (coding, cooking) NOT in the books, politely state: "This topic is outside my library, but here is a general answer:" and follow the standard format as best as possible.
"""

QUERY_GEN_PROMPT = (
    "You are an expert research assistant. Your goal is to generate 3 distinct search queries to maximize the retrieval of relevant information.\n"
    "Input Query: {query}\n"
    "Instructions:\n"
    "1. Include the user's original query exactly as is.\n"
    "2. Generate 2 additional queries that explore different angles, synonyms, or related concepts.\n"
    "3. Ensure the queries are diverse and not just minor rephrasings.\n"
    "Output each query on a separate line."
)

class LoggingPostprocessor(BaseNodePostprocessor):
    """Custom Postprocessor to log nodes for debugging/inspection."""
    label: str = "Nodes"

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[object] = None,
    ) -> List[NodeWithScore]:
        print(f"\n--- LOG: {self.label} ({len(nodes)} retrieved) ---")
        for i, node in enumerate(nodes[:5]):  # Print top 5 to avoid clutter
            score = f"{node.score:.4f}" if node.score is not None else "None"
            content_preview = node.node.get_content()[:100].replace('\n', ' ')
            print(f"[{i+1}] Score: {score} | {content_preview}...")
        if len(nodes) > 5:
            print(f"... and {len(nodes) - 5} more.")
        print("------------------------------------------------\n")
        return nodes

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

    # 3. Rerank & Logging
    node_postprocessors = []
    
    # Log BEFORE Re-ranking
    node_postprocessors.append(LoggingPostprocessor(label="Retrieved (Pre-Rerank)"))

    if COHERE_API_KEY:
        # User requested keeping top_n=10
        cohere_rerank = CohereRerank(api_key=COHERE_API_KEY, top_n=10)
        node_postprocessors.append(cohere_rerank)
        
        # Log AFTER Re-ranking
        node_postprocessors.append(LoggingPostprocessor(label="Selected (Post-Rerank)"))

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
