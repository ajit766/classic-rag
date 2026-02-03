# Technical Stack & Requirements

## 1. Frontend Scope
-   **Framework**: Next.js 14+ (App Router).
-   **Styling**: Tailwind CSS (Shadcn/UI aesthetics).
-   **State**: React Hooks + Vercel AI SDK (`useChat`).
-   **Deployment**: Vercel (CI/CD via GitHub).

## 2. Backend Scope
-   **Language**: Python 3.10+.
-   **Framework**: FastAPI (Async support).
-   **Orchestration**: LlamaIndex (RAG Logic, Node Parsing).
-   **Deployment**: Render.com (Web Service, auto-deploy).

## 3. AI & Data Infrastructure
-   **LLM**: OpenAI GPT-4o (Reasoning & Synthesis).
-   **Embeddings**: OpenAI `text-embedding-3-small` (1536 dims).
-   **Vector DB**: Pinecone Serverless (us-east-1).
-   **Re-ranking**: Cohere Re-rank v3 (Filtering).
-   **Observability**: Langfuse (Tracing & Evaluation).
