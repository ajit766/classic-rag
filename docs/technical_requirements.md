# Technical Requirements Document: "The Modern Sage"

## 1. System Architecture Style
-   **Hybrid RAG (Retrieval-Augmented Generation)**: Uses a combination of dense vector semantic search and keyword-based search to handle both abstract concepts and specific terminology.
-   **Client-Server Decoupling**: Frontend is strictly a presentation layer; all business logic and RAG orchestration reside in the Python backend.

## 2. Tech Stack

### Core Backend (API & Orchestration)
-   **Language**: Python 3.10+
-   **Web Framework**: FastAPI
-   **RAG Orchestrator**: LlamaIndex (preferred for structured data handling capabilities)
-   **API Standard**: RESTful endpoints

### Frontend (User Interface)
-   **Framework**: Next.js (App Router)
-   **Language**: TypeScript
-   **Styling**: Tailwind CSS
-   **State Management**: **Vercel AI SDK** (providing `useChat` for robust streaming and optimistic UI updates).

### Data & Infrastructure
-   **Vector Cloud DB**: Pinecone (Serverless)
-   **Embeddings**: OpenAI `text-embedding-3-small` (or similar high-performance model)
-   **LLM**: OpenAI `gpt-4o` or `gpt-3.5-turbo` / Gemini 1.5 Pro
-   **Local Storage**: Local filesystem for raw PDF storage (for ingestion scripts)

## 3. Functional Requirements

### 3.1. Data Ingestion Pipeline
-   Must accept PDF files.
-   Must parse text and chunk it intelligently (e.g., overlapping windows of 512 tokens).
-   Must embed chunks and upsert to Pinecone with metadata (`book_title`, `page_number`, `type: science/spiritual`).

### 3.2. Search & Retrieval
-   **Hybrid Search**: Combine Vector Similary + Keywork (BM25) matching.
-   **Re-ranking**: Re-rank retrieved nodes to prioritize the most relevant context.
-   **Top-K**: Retrieve at least 5-10 chunks to ensure enough context for both perspectives.

### 3.3. API Endpoints
-   `POST /api/chat`: streamable endpoint accepting `{ query: string, history: [] }`.
-   `POST /api/ingest`: Admin endpoint to trigger ingestion of new files.

## 4. Non-Functional Requirements
-   **Latency**: Initial response stream start < 2 seconds.
-   **Reliability**: Graceful fallback if retrieval fails (e.g., "I couldn't find specific info in the books, but based on general knowledge...").
-   **Security**: API Keys (OpenAI, Pinecone) stored in `.env`. No hardcoding.
