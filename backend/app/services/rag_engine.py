
import logging
from typing import List, Optional
from llama_index.core.llms import ChatMessage
from llama_index.core import VectorStoreIndex
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
from llama_index.core import set_global_handler

from app.core.config import settings

logger = logging.getLogger("app.services.rag")

# Re-using the prompt constants from the original file
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

**Relevance & Conversational Check**:
*   **Conversational Queries** (e.g., "Hi", "Who are you?"): Reply naturally and politely as "The Modern Sage". Do NOT use the citations or the Dual-Perspective structure.
*   **Out-of-Scope Queries** (e.g., "How to bake a cake", "Python code"): Politely decline, stating: "I am designed to answer questions about Wisdom and Psychology based on my library. I cannot assist with this specific topic." Do NOT generate a generic answer.
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
        logger.debug(f"--- LOG: {self.label} ({len(nodes)} retrieved) ---")
        for i, node in enumerate(nodes[:5]):
            score = f"{node.score:.4f}" if node.score is not None else "None"
            content_preview = node.node.get_content()[:100].replace('\n', ' ')
            logger.debug(f"[{i+1}] Score: {score} | {content_preview}...")
        return nodes

class ChatService:
    _instance = None
    _chat_engine = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the RAG pipeline once."""
        logger.info("Initializing ChatService and RAG Pipeline...")
        
        # Observability
        if settings.LANGFUSE_SECRET_KEY:
            try:
                set_global_handler("langfuse", 
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    host=settings.LANGFUSE_HOST
                )
                logger.info("Langfuse Observability Enabled")
            except Exception as e:
                logger.warning(f"Failed to init Langfuse: {e}")

        # Vector Store
        if not settings.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not found in settings")
            
        # LLM & Embedding Config
        import llama_index.core
        from llama_index.embeddings.openai import OpenAIEmbedding

        embed_model = OpenAIEmbedding(api_key=settings.OPENAI_API_KEY)
        llama_index.core.Settings.embed_model = embed_model
        llama_index.core.Settings.llm = OpenAI(model="gpt-4o", api_key=settings.OPENAI_API_KEY)

        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        pinecone_index = pc.Index(settings.INDEX_NAME)
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)

        # LLM
        # LLM - Get from Settings
        llm = llama_index.core.Settings.llm
        # or re-init if specific params needed, but we set it globally above.
        # Let's keep using the one we set to be consistent.

        # Retrievers
        vector_retriever = index.as_retriever(similarity_top_k=15)
        
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

        # Postprocessors
        node_postprocessors = []
        node_postprocessors.append(LoggingPostprocessor(label="Retrieved (Pre-Rerank)"))

        if settings.COHERE_API_KEY:
            cohere_rerank = CohereRerank(api_key=settings.COHERE_API_KEY, top_n=10)
            node_postprocessors.append(cohere_rerank)
            node_postprocessors.append(LoggingPostprocessor(label="Selected (Post-Rerank)"))
        else:
            logger.warning("COHERE_API_KEY not found. Reranking disabled.")

        # Chat Engine
        self._chat_engine = ContextChatEngine.from_defaults(
            retriever=fusion_retriever,
            memory=ChatMemoryBuffer.from_defaults(token_limit=4000),
            llm=llm,
            system_prompt=SYSTEM_PROMPT,
            node_postprocessors=node_postprocessors,
            verbose=True
        )
        logger.info("ChatService Initialized.")

    def get_chat_engine(self):
        return self._chat_engine

# Singleton accessor
def get_chat_service() -> ChatService:
    return ChatService()
