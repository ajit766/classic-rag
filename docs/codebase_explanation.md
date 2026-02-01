# Codebase Explanation: The Modern Sage

This document provides a technical deep-dive into the source code of "The Modern Sage".

## Directory Structure
```
classic-rag/
├── backend/               # Python FastAPI Server
│   ├── data/             # PDF storage for ingestion
│   ├── ingest.py         # Script to populate Vector DB
│   ├── main.py           # API Entry point
│   ├── rag_engine.py     # Core RAG Logic
│   └── requirements.txt  # Python Dependencies
├── frontend/             # Next.js Application
│   ├── app/              # App Router Pages
│   └── components/       # React Components (Chat UI)
└── docs/                 # Design Documents
```

---

## Backend (`/backend`)

### 1. `rag_engine.py` (The Brain)
This file defines the intelligence of the system.
*   **Purpose**: Connects to Pinecone and initializes the LlamaIndex Chat Engine.
*   **Key Logic**:
    *   `SYSTEM_PROMPT`: This is where the persona is defined. It strictly instructs the LLM to adopt a "Dual Perspective" (Science + Spirituality) and enforce citations.
    *   `get_chat_engine()`:
        *   Initializes `PineconeVectorStore` using the API key.
        *   Creates a `ChatMemoryBuffer` (limit 3000 tokens) so the bot remembers context from previous turns.
        *   Returns a `chat_engine` configured in `context` mode (it retrieves context first, then answers).

### 2. `ingest.py` (The Knowledge Loader)
*   **Purpose**: Runs once (offline) to parse PDFs and upload them to the database.
*   **Key Logic**:
    *   `SimpleDirectoryReader("./data").load_data()`: LlamaIndex utility that automatically converts PDFs into text objects.
    *   `VectorStoreIndex.from_documents()`:
        1.  Splits text into chunks (default ~1024 tokens).
        2.  Calls OpenAI to generate Embeddings (vectors) for each chunk.
        3.  Upserts these vectors into your Pinecone index.

### 3. `main.py` (The API Layer)
*   **Purpose**: Exposes the logic to the web via HTTP.
*   **Key Logic**:
    *   `/api/chat` endpoint:
        *   Accepts a JSON body `{ messages: [...] }`.
        *   Converts the frontend message format into LlamaIndex `ChatMessage` objects.
        *   Calls `chat_engine.stream_chat(query)`.
    *   **Streaming Protocol**:
        *   The `event_generator()` function transforms the raw text stream into the **Vercel AI SDK Protocol**.
        *   Format: `0:"{token}"\n`. This allows the frontend to display text effect "typing" in real-time.

---

## Frontend (`/frontend`)

### 1. `components/ChatInterface.tsx` (The UI)
*   **Purpose**: Main chat view.
*   **Key Library**: `ai/react` (Vercel AI SDK).
*   **Key Logic**:
    *   `useChat({ api: ... })`: This hook handles *everything* related to chat state.
        *   It automatically appends the user's message to `messages` array immediately (Optimistic UI).
        *   It handles the POST request to the backend.
        *   It decodes the streaming response and updates the `messages` array token-by-token.
    *   **Error Handling**: We expose the `error` object from the hook to display alerts if the backend fails.
    *   **Auto-Scroll**: A `useEffect` hook triggers `scrollIntoView` whenever `messages` change, keeping the chat at the bottom.

### 2. `app/page.tsx`
*   **Purpose**: Simple wrapper that renders `ChatInterface`. This is a Server Component by default, but it imports the Client Component `ChatInterface`.
