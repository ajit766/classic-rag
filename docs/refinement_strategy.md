# Refinement Strategy: "The Modern Sage" v2

## 1. Product Goals & Acceptance Criteria (AC)

### Goal A: Exhaustiveness & Detail
**User Story**: "As a user, when I ask a question, I want to see multiple perspectives and citations so that I feel the answer is deeply researched."
**Acceptance Criteria**:
1.  **Citation Density**: The response must contain **at least 3 unique citations** (distinct books or distinct chapters) if the corpus supports it.
2.  **Balance**: Ideally, at least 1 citation from "Science" and 1 from "Spirituality" for broad questions.
3.  **Depth**: The model should not just quote one sentence but synthesize the *concept* from multiple retrieved chunks.

### Goal B: Graceful Fallback (Scope Management)
**User Story**: "As a user, when I ask about coding or general topics, I don't want forced, irrelevant book quotes."
**Acceptance Criteria**:
1.  **Relevance Check**: If the retrieved chunks have low similarity (e.g., I ask "How to bake a cake"), the system should NOT force a connection to *Atomic Habits*.
2.  **Behavior**:
    *   *In-Scope*: Rich answer with citations.
    *   *Out-of-Scope*: Standard helpful LLM answer (without "As mentioned in Bhagavad Gita...").

---

## 2. Technical Implementation Plan (Advanced RAG Architecture)

### A. Data Ingestion Upgrade (Better Context)
*   **Problem**: Fixed-size chunks cut off ideas mid-flow.
*   **Solution**: **Semantic Chunking** (`SemanticSplitterNodeParser`).
    *   Uses embeddings to detect "topic breaks" in the text.
    *   Creates variable-sized chunks that represent complete thoughts.
    *   *Action*: Update `ingest.py` and re-index all PDFs.

### B. Retrieval Pipeline Upgrade (Exhaustiveness)
*   **Problem**: Standard search only finds text matching the literal query.
*   **Solution**: **Query Decomposition & Re-ranking**.
    1.  **Query Transformation**: Use LLM to generate 2 sub-queries:
        *   "Scientific aspect of [topic]"
        *   "Spiritual aspect of [topic]"
    2.  **Parallel Retrieval**: Fetch `top_k=10` for *each* sub-query (Total 20 chunks).
    3.  **Re-ranking**: Use `bge-reranker-base` to score these 20 chunks by relevance and pick the **Top 10**.
    4.  *Benefit*: Guarantees we have content from both sides, filtered for quality.

### C. Guardrails (Scope Management)
*   **Problem**: System hallucinates connections for irrelevant queries ("How to code").
*   **Solution**: **Soft Prompt Fallback**.
    *   Instead of a complex Router (which proved brittle), we rely on a Strict System Prompt.
    *   **Mechanism**: The LLM is instructed: *"If the user asks about a general topic... state: 'This topic falls outside my library' and answer generally."*
    *   **Verification**: Tested with queries like "Write a binary search script", returning standard coding answers without forced citations.

### D. Generation (Citations)
*   **Problem**: Citations are sometimes missing.
*   **Solution**:
    *   With **Top-10** high-quality chunks (thanks to Re-ranking), the LLM has plenty of source material.
    *   Update System Prompt to strictly enforce: "If you use a chunk, you MUST output [Book Name]"


---

## 3. Recommended Plan (The "Portfolio" Approach)

To show depth for your portfolio, I recommend:

1.  **Implement Re-ranking (`bge-reranker-base`)**: This solves "Exhaustiveness" by finding the *best* 5-7 chunks from a larger pool. It proves you understand Advanced RAG.
2.  **Implement a Router**: This solves "Fallback". A simple "Guardrail" step.
3.  **Update System Prompt**: Explicitly instruct: "If the provided context is not relevant to the query, DO NOT force a citation. Answer from general knowledge."

## 4. Evaluation (Evals)
How do we know it works?

*   **Test Case A (Depth)**: "How do I overcome fear?"
    *   *Pass*: Contains quotes from Gita AND Atomic Habits/Thinking Fast Slow.
*   **Test Case B (Fallback)**: "Write a Python script for a binary search."
    *   *Pass*: Helpful code, NO mention of "Dharma" or "Habits".
