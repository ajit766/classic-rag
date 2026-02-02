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
We moved away from fixed-size characters to **Semantic Splitting**.
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
