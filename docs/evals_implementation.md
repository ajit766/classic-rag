# Evaluation Implementation & Analysis

## 1. Goal: Evidence-Based Engineering
In RAG systems, "vibes" are insufficient. I implemented a quantitative evaluation pipeline to measure:
1.  **Faithfulness**: Is the answer hallucinated? (Does it strictly follow the retrieved context?)
2.  **Relevancy**: Does the answer actually address the user's question?

## 2. Implementation: `backend/evals/evaluate.py`
Instead of manually writing test cases, I built a self-generating pipeline:

### The "Golden Dataset" Generation
1.  **Sampling**: The script selects random chunks from the Pinecone index.
2.  **Synthesis**: It uses GPT-4 to generate a "Ground Truth Question" that the chunk *should* be able to answer.
    *   *Example*: From a chunk about "Tamasic nature," GPT-4 generates: "How does the Bhagavad Gita describe the mode of ignorance?"

### The LLM-as-a-Judge Loop
1.  **Execution**: The system runs the *generated question* through the full RAG pipeline (Retrieval -> Fusion -> Generation).
2.  **Grading**: A separate GPT-4 instance acts as the impartial judge.
3.  **Metrics**:
    *   **Faithfulness Score (0-1)**: Checks if every claim in the answer is supported by the retrieved context.
    *   **Relevancy Score (0-1)**: Checks if the answer satisfies the original question.

## 3. Results & Analysis (Current Status)

| Metric | Score | Analysis |
| :--- | :--- | :--- |
| **Faithfulness** | **80%** | The system generally sticks to the text. Failures occur when the "Strict Dual-Perspective" prompt forces the LLM to invent a "Scientific" connection for a purely spiritual question. |
| **Relevancy** | **100%** | High. The Fusion Retriever successfully finds the right context. |

### Why 80%? (The "Strict Prompt" Trade-off)
The current `SYSTEM_PROMPT` enforces a rigid structure:
> "You MUST provide a Spiritual Perspective AND a Scientific Perspective."

*   **The Conflict**: If a user asks a purely technical question (e.g., "What is the study on Contextual Priming?"), the LLM is forced to also provide a "Spiritual Perspective."
*   **The Verdict**: The strict judge flags this extra spiritual content as "Irrelevant" to the scientific question, lowering the score.
*   **Next Step**: Relax the prompt to "Provide both perspectives **where applicable**" to improve automated scores, though this risks losing the "Modern Sage" persona consistency.(TBD)
