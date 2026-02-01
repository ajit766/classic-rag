# Implementation Plan: The Modern Sage

# Goal Description
Build a Hybrid RAG application "The Modern Sage" that answers user queries by synthesizing insights from scientific self-help books and the Bhagavad Gita, with accurate citations.

## User Review Required
> [!IMPORTANT]
> **API Keys Needed**: You will need a **Pinecone API Key** and an **OpenAI API Key** (or Gemini/Anthropic) to run this.
> **PDF Files**: You need to provide the actual PDF files for the books (Atomic Habits, Gita, etc.) locally for ingestion. I cannot generate the book content myself.

## Proposed Changes

### Backend (Python/FastAPI)
Structure: `backend/`
#### [NEW] `backend/main.py`
- Setup FastAPI app.
- Define API endpoints: `/chat`, `/ingest` (admin only).
- Initialize LlamaIndex query engine.

#### [NEW] `backend/rag_engine.py`
- **Ingestion**: Function to read PDFs from a `data/` directory.
- **Indexing**: Code to parse text, create nodes, and upload vectors to Pinecone.
- **Retrieval**: Configure `VectorStoreIndex` with specific parameters for Hybrid Search (if supported by Pinecone/LlamaIndex config directly) or ensure high-quality dense retrieval.
- **Query Engine**: Setup the prompt template that instructs the LLM to act as the "Sage" and provide citations.

#### [NEW] `backend/requirements.txt`
- `fastapi`, `uvicorn`, `llama-index`, `python-dotenv`, `pinecone-client`, `llama-index-vector-stores-pinecone`.

### Frontend (Next.js)
Structure: `frontend/`
#### [NEW] `frontend/components/ChatInterface.tsx`
- Chat UI with message bubbles.
- Handling distinct "Science" vs "Spirituality" sections if we shape the JSON response that way, or just rendering markdown.
- Display "Sources" component.

#### [NEW] `frontend/app/page.tsx`
- Main entry point.

### Infrastructure & Data
#### [NEW] `backend/data/`
- Directory where you will place your PDFs.

## Verification Plan

### Automated Tests
- We will script a simple `test_rag.py` to run a query like "How to focus?" and assert that:
    1.  Response is generated.
    2.  Source nodes are returned in the metadata.

### Manual Verification
- **Ingestion Test**: Run the ingestion script and check the Pinecone dashboard for vector count.
- **Chat Test**: Run the full stack (`uvicorn` + `npm run dev`), ask a question, and verify the answer contains references to *both* types of books.
