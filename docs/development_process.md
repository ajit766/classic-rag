# Development Process & Engineering Standards

## 1. How I Used AI (Transparent Disclosure)
This project leverages AI not just as the *product*, but as a *force multiplier* in the development process. Here is the breakdown:

### A. Co-Pilot, Not Autopilot
*   **Architecture**: **I manually designed** the "Strict Dual-Perspective" system prompt and the Fusion logic. The decision to enforce specific citation quotas ("2 from Gita, 3 from Science") was a product decision I made to ensure the "Modern Sage" persona felt authentic.
*   **Boilerplate**: I used AI to generate the initial Next.js UI components (Tailwind classes are tedious to type).
*   **Synthetic Data**: I heavily used AI to generate the *test cases* in `evaluate.py`. Writing 50 questions manually is poor use of engineering time. I directed the AI to "Generate questions that target the intersection of Science and Spirituality."

---

## 2. Engineering Standards

### A. Observability (Trace or it didn't happen)
I integrated **Langfuse** to monitor the app in production.
*   **Why**: RAG is non-deterministic. "It feels slow" is not a bug report; "Retrieval took 800ms" is actionable data.
*   **Implementation**: Used `set_global_handler("langfuse")`.
*   **Captures**: Latency per step (Retrieval vs Gen), Token usage, and full Trace trees.

### B. Type Safety & Clean Code
*   **Backend**: Python 3.10+ with explicit Type Hints (e.g., `List[NodeWithScore]`).
*   **Frontend**: TypeScript (Next.js) for props validation.
*   **Modular Structure**:
    *   `ingest.py`: Dedicated ETL pipeline.
    *   `rag_engine.py`: Encapsulated Core Logic.
    *   `main.py`: Thin API Layer.
