# System Architecture: "The Modern Sage"

## High-Level Component Diagram

```mermaid
graph TD
    subgraph "Frontend Layer (Next.js)"
        UI[Web UI / Chat Interface]
        State[Chat State Manager]
    end

    subgraph "Backend Layer (FastAPI)"
        API[API Endpoints /chat]
        Orch[LlamaIndex Orchestrator]
        Ingest[Ingestion Service]
    end

    subgraph "Data & AI Layer"
        Pinecone[(Pinecone Vector DB)]
        LLM[LLM (OpenAI/Gemini)]
        Files[Raw PDFs]
    end

    %% Interactions
    UI <-->|"JSON Stream"| API
    API --> Orch
    Orch <-->|"Retrieve & Re-rank"| Pinecone
    Orch <-->|"Generate"| LLM
    Ingest -->|"Parse & Chunk"| Files
    Ingest -->|"Embed & Upsert"| Pinecone
```

## Detailed Data Flows

### 1. Ingestion Flow (Offline / Admin Trigger)
How books get into the "Brain".

```mermaid
sequenceDiagram
    participant Admin
    participant IngestService as Ingestion Script
    participant Parser as PDF Parser
    participant Embed as Embedding Model
    participant DB as Pinecone

    Admin->>IngestService: Trigger Ingestion (folder path)
    loop For each PDF
        IngestService->>Parser: Extract Text
        Parser-->>IngestService: Raw Text
        IngestService->>IngestService: Chunk Text (Overlap) & Add Metadata
        IngestService->>Embed: Generate Embeddings (Chunks)
        Embed-->>IngestService: Vectors
        IngestService->>DB: Upsert Vectors + Metadata
    end
    IngestService-->>Admin: Success (Count)
```

### 2. RAG Query Flow (Runtime)
How a user question becomes an answer.

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend
    participant API as FastAPI Backend
    participant Engine as LlamaIndex Engine
    participant DB as Pinecone
    participant LLM as OpenAI/Gemini

    User->>UI: "How to stop procrastinating?"
    UI->>API: POST /chat (query)
    API->>Engine: Query(query_text)
    
    par Dual Search
        Engine->>DB: Vector Search (Semantic)
        Engine->>DB: Keyword Search (BM25)
    end
    
    DB-->>Engine: Raw Nodes (Chunks)
    Engine->>Engine: Re-rank Nodes (Re-ranker)
    
    Engine->>LLM: Prompt + Top-K Context
    Note over LLM: System Prompt enforces<br/>"Science + Spirit" Synthesis
    LLM-->>Engine: Generated Response
    Engine-->>API: Stream Response
    API-->>UI: Stream Tokens
    UI->>User: Displays Answer + Citations
```
