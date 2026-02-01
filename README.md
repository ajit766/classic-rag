# The Modern Sage 🧘‍♂️🔬

A Hybrid RAG (Retrieval-Augmented Generation) AI Assistant that blends **Modern Behavioral Science** with **Timeless Spiritual Wisdom**.

## Project Overview
This tool helps users solve life problems by synthesizing advice from sources like *Atomic Habits* (Science) and *The Bhagavad Gita* (Spirituality).

**Tech Stack**:
*   **Frontend**: Next.js, Tailwind CSS, Vercel AI SDK.
*   **Backend**: Python, FastAPI, LlamaIndex.
*   **Database**: Pinecone (Vector DB) + OpenAI Embeddings.

## Quick Start

### Prerequisites
*   Node.js & npm
*   Python 3.10+
*   OpenAI API Key
*   Pinecone API Key

### 1. Setup Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with your keys
cp .env.example .env 
```

### 2. Ingest Data (First Time Only)
Place your PDF files in `backend/data/`, then run:
```bash
python3 ingest.py
```

### 3. Run Servers
**Backend:**
```bash
# In backend/ directory
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to chat!

## Architecture
See `docs/architecture.md` for a visual diagram of the system.
