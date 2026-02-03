# System Architecture: "The Modern Sage"

## High-Level Component Diagram

```mermaid
graph TD
    subgraph "Frontend (Vercel)"
        UI[Next.js Chat Interface]
    end

    subgraph "Backend (Render)"
        API[FastAPI /chat]
        Engine[RAG Engine]
        Fusion[Query Fusion Module]
        Rerank[Cohere Re-ranker]
    end

    subgraph "Data Layer"
        Pinecone[(Pinecone Serverless DB)]
        Cohere[Cohere API]
        OpenAI[OpenAI GPT-4o]
        Langfuse[Langfuse Observability]
    end

    %% Interactions
    UI <-->|"Stream"| API
    API --> Engine
    Engine -->|"1. Generate Queries"| OpenAI
    Engine -->|"2. Parallel Search"| Pinecone
    Pinecone -->>|"30 Chunks"| Engine
    Engine -->|"3. Re-rank (Top 10)"| Rerank
    Rerank -->>|"Top 10 Chunks"| Engine
    Engine -->|"4. Synthesize"| OpenAI
    OpenAI -->>|"Response"| UI
```

## Detailed Pipelines

### 1. Ingestion Flow (Semantic Chunking)
We moved away from fixed-size characters(in V1) to **Semantic Splitting**.
1.  **Parser**: Extracts text from PDFs.
2.  **Semantic Splitter**: `SemanticSplitterNodeParser` (LlamaIndex).
    *   Uses OpenAI Embeddings to detect "topic shifts" in the text.
    *   Splits only when the semantic meaning changes (Percentile 95).
3.  **Vector Store**: Upserts to Pinecone (1536 dim).

### 2. Retrieval Flow (Advanced RAG)
How a user question becomes an answer.

1.  **Query Decomposition (Dynamic Research)**:
    -   Input: "Why am I lazy?"
    -   LLM Generates 3 Queries:
        1.  "Why am I lazy?" (Original)
        2.  "Causes of chronic procrastination and lack of motivation" (Angle 1: Clinical/Scientific)
        3.  "Overcoming Tamas and finding purpose in duty" (Angle 2: Philosophical/Spiritual relevant concept)
    -   *Benefit*: Instead of forcing "Science vs Spirit", the AI dynamically generates the most relevant research angles for the specific question.

2.  **Parallel Retrieval**:
    -   The system runs vector search for *all 3 queries*.
    -   Pool size: Top 30 documents.

3.  **Re-ranking (Cohere)**:
    -   The `CohereRerank` model takes the 30 candidate chunks and the original query.
    -   It assigns a relevance score (0-1) to each.
    -   **Top 10** are selected. This filters out irrelevant "noise" from the broad search.

4.  **Generation (Dual-Perspective)**:
    -   GPT-4o receives the Top 10 chunks.
    -   **System Prompt**: Enforces the "Strict Dual-Perspective" structure (Spiritual vs. Scientific) with citation quotas.
    -   **System Prompt**: Enforces the "Strict Dual-Perspective" structure (Spiritual vs. Scientific) with citation quotas.

## Technical Decisions & Trade-offs

I approached this assignment not just to "make it work," but to build a **production-grade baseline**. Here is the reasoning behind every major component choice, including the alternatives I considered and rejected.

### 1. The RAG Engine (Orchestrator): LlamaIndex vs LangChain
*   **Selected**: **LlamaIndex**
*   **Considered**: LangChain
*   **Reasoning**: LlamaIndex is currently superior for **Data Ingestion** and **Retrieval** complexity. Its `SemanticSplitterNodeParser` and native support for `QueryFusionRetriever` allowed me to implement "Advanced RAG" patterns (Chunking + Fusion) with significantly less boilerplate than LangChain. LangChain is great for agents, but LlamaIndex wins for pure RAG quality.

### 2. Retrieval Strategy: Semantic Fusion vs Standard Density
*   **Selected**: **Hybrid Search + Query Decomposition + Re-ranking**
*   **Considered**: Simple Cosine Similarity, Keyword Search (bm25)
*   **Reasoning**:
    *   *The Problem*: Users ask vague questions ("Why am I lazy?"). A simple vector search might miss specific psychological terms.
    *   *The Solution*: I implemented a **Fusion** layer. The LLM expands the query into 3 angles: (1) Original, (2) Clinical Psychology terms, (3) Spiritual concepts.
    *   *The Trade-off*: This adds latency (~800ms generation time) but increases **Recall** dramatically.

### 3. Chunking Strategy: Semantic vs Fixed-Size
*   **Selected**: **Semantic Chunking** (Percentile 95)
*   **Considered**: Fixed-Size (e.g., 500 chars), Recursive Character Split
*   **Reasoning**:
    *   *The Problem*: Fixed chunking often cuts sentences in half or separates a header from its content ("Chapter 1" ... [cut] ... "Introduction").
    *   *The Solution*: Semantic splitting uses embeddings to detect "topic shifts" and breaks text only when the meaning changes.
    *   *The Trade-off*: Slower ingestion (requires embedding every sentence), but much higher quality context for the LLM.

### 4. Vector Database: Pinecone Serverless vs Postgres (pgvector)
*   **Selected**: **Pinecone Serverless**
*   **Considered**: PGVector, ChromaDB (Local)
*   **Reasoning**:
    *   *The Problem*: Managing vector infrastructure is painful (OOM errors, scaling pods).
    *   *The Solution*: Pinecone Serverless decouples storage from compute. It scales to zero (cost-effective) and provides <100ms P99 latency.
    *   For this project, I also wanted to demonstrate cloud-native architectural patterns and pinecone is one of the best.

### 5. Re-ranking: Cohere vs No Re-ranker
*   **Selected**: **Cohere Re-rank (v3)**
*   **Considered**: Cross-Encoders (SentenceTransformers), No Re-ranking
*   **Reasoning**:
    *   *The Design*: The Retriever casts a wide net (Top 30 chunks) to maximize recall.
    *   *The Filter*: Cohere Re-rank scores them for relevance and picks the Top 10.
    *   *Impact*: This priority has a significance impact(can be measured as well) and the cost of implementation is also less.
