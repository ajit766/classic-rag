# Codebase Explanation: "The Modern Sage"

This document provides a detailed technical breakdown of the "Modern Sage" RAG application. It explains the core components, their purpose, and the **exact default configurations** used in production.

---

## 1. Backend: Data Ingestion (`backend/ingest.py`)

**Purpose**: This script runs once (or on-demand) to process raw PDFs and load them into the Vector Database.

### Key Components & Defaults
*   **Semantic Chunking**: Instead of arbitrarily cutting text every 500 characters, we use AI to find "conceptual breaks" in the text.
    *   **Class**: `SemanticSplitterNodeParser`
    *   **Default**: `breakpoint_percentile_threshold=95` (Very strict; only splits when the topic shifts significantly).
    *   **Buffer Size**: `1` (Keeps one sentence of overlap for context continuity).
*   **Embedding Model**: `OpenAIEmbedding` (text-embedding-3-small).
*   **Vector Database**: `PineconeVectorStore`.
    *   **Index Name**: `modern-sage`
    *   **Dimension**: `1536` (Matches OpenAI embeddings).
    *   **Metric**: `cosine`.

---

## 2. Backend: RAG Engine (`backend/rag_engine.py`)

**Purpose**: The "Brain" of the application. It creates the Chat Engine that handles user queries, retrieval, and generation.

### Pipeline Steps & Configuration

#### A. Retrieval (Query Fusion)
We use a **Fusion Retriever** to expand the search scope.
*   **Input**: User query (e.g., "Purpose of life").
*   **Decomposition**: The LLM generates **3 queries**:
    1.  Original Query.
    2.  Scientific/Psychological variation.
    3.  Spiritual/Philosophical variation.
*   **Retrieval**: It searches Pinecone for *all 3 queries*.
*   **Pool Size**: `similarity_top_k=30` (It fetches the top 30 chunk candidates in total).

#### B. Post-Processing (Re-ranking)
We refine the broad pool of 30 chunks down to the absolute best ones.
*   **Tool**: `CohereRerank` (Model: `rank-english-v3.0` via API).
*   **Top N Default**: `top_n=10` (Only the top 10 most relevant chunks are passed to GPT-4).
    *   *Why 10?* Enough context to synthesize 5-6 citations without overflowing the context window.

#### C. Generation (LLM)
*   **Model**: `gpt-4o`.
*   **Temperature**: `0.7` (Balances creativity with factual accuracy).
*   **Memory**: `ChatMemoryBuffer` with `token_limit=4000` (Remembers roughly the last 3-4 turns of conversation).
*   **System Prompt**: Enforces a **Strict Dual-Perspective** structure:
    1.  **Spiritual Perspective**: Required 2-3 citations (e.g., *Bhagavad Gita*).
    2.  **Scientific Perspective**: Required 3-4 citations (e.g., *Atomic Habits*, *Ikigai*).

---

## 3. Backend: API Server (`backend/main.py`)

**Purpose**: Exposes the RAG logic as a REST API for the frontend.

### Endpoints
*   `POST /api/chat`: The main endpoint.
    *   **Input**: JSON `{ messages: [...] }`.
    *   **Processing**: Converts the last user message into a query for `rag_engine`.
    *   **Response**: **Streaming Response** (Server-Sent Events).
    *   **Format**: Vercel AI SDK Protocol (`0:{text_chunk}\n`).

---

## 4. Frontend: User Interface (`frontend/components/ChatInterface.tsx`)

**Purpose**: A React component that handles the chat state and renders the streaming response.

### Tech Stack
*   **Framework**: Next.js 14+ (App Router).
*   **Library**: `ai/react` (Vercel AI SDK).
*   **Styling**: Tailwind CSS.

### Key Logic
*   **State Management**: `useChat` hook handles `messages`, `input`, `isLoading`, and `error`.
*   **API Connection**:
    *   **Production**: Uses `process.env.NEXT_PUBLIC_API_URL` (Points to Render).
    *   **Development**: Defaults to `http://localhost:8000/api/chat`.
*   **Rendering**:
    *   Markdown support via `react-markdown` (implied in usage, or standard text rendering).
    *   Auto-scrolling using `messagesEndRef`.

---

## Summary of Critical Defaults

| Component | Setting | Value | Reason |
| :--- | :--- | :--- | :--- |
| **Splitting** | Percentile | `95` | Keeps related concepts together in one chunk. |
| **Retrieval** | Schemes | `3` | 1 Original + 1 Science + 1 Spirit. |
| **Fusion** | Top K | `30` | Broad initial net to catch everything relevant. |
| **Re-rank** | Top N | `10` | High-precision filtering for the LLM. |
| **Memory** | Token Limit | `4000` | Approx ~15 mins of reading context. |
| **LLM** | Temperature | `0.7` | Good mix of "Sage-like" wisdom and accuracy. |
