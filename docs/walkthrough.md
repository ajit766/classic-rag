# Walkthrough: The Modern Sage

"The Modern Sage" is a RAG-based AI assistant that synthesizes advice from scientific self-help books and the Bhagavad Gita.

## Features Implemented
1.  **Hybrid Knowledge Base**: Indices content from *Atomic Habits*, *Thinking, Fast and Slow*, and *The Bhagavad Gita*.
2.  **"Dual Perspective" Engine**: Custom RAG logic that instructs the AI to blend scientific strategy with spiritual wisdom.
3.  **Real-time Streaming**: A responsive Chat UI built with Next.js and Vercel AI SDK that streams answers token-by-token.
4.  **Citations**: The AI explicitly cites the books it references in its answers.

## Architecture Verification
-   **Backend**: Python/FastAPI server running on port `8000`.
-   **Vector DB**: Pinecone Serverless Index (`modern-sage`) containing ~1880 embeddings.
-   **Frontend**: Next.js App Router application running on port `3000`.

## Setup & Run Instructions
To restart the project in the future:

### 1. Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Frontend
```bash
# In a new terminal
cd frontend
npm run dev
```

## Version 2: Advanced RAG
We significantly enhanced the retrieval pipeline to ensure "Exhaustiveness" and "Deep Context".

### Key Features
1.  **Semantic Chunking**:
    *   Replaced fixed-size chunks with AI-driven "Semantic Splits".
    *   The model now reads sentence-by-sentence to keep complete thoughts together.
2.  **Query Decomposition (Fusion)**:
    *   For every user question, the system generates **3 variations**:
        1.  Original Query
        2.  "Scientific/Psychological aspect..."
        3.  "Spiritual/Philosophical aspect..."
    *   This ensures we retrieve content from *both* domains (e.g. Atomic Habits AND The Gita).
3.  **Cohere Re-ranking**:
    *   We retrieve a broad set of **30 chunks**.
    *   A specialized "Re-ranker Model" (Cohere) grades them and selects the **Top 10** most relevant ones.
    *   This filters out noise and guarantees high-quality context.

## Validation
-   [x] **Ingestion**: 5 PDFs successfully chunked and uploaded to Pinecone.
-   [x] **API**: `/api/chat` endpoint accepts JSON and returns a valid Data Stream.
-   [x] **UI**: Chat interface connects, displays streaming text, and handles user input.
-   [x] **Deployment**: Frontend Configured for Vercel, Backend for Render.
