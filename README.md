# The Modern Sage: Dual-Perspective RAG Assistant

## **What is this?**
A conversational assistant which acts as a self-help coach/guide on any life problems by synthesizing Modern texts like 7-habits of highly effective people, Atomic habits, ikigai, and Ancient Wisdom texts like Bhagavad Gita/Bible.

## **Why is this made?**
While a standard LLM can answer questions, it cannot provide authentic information. It can only provide information based on the data it has been trained on and we don't know what it has been trained on and hence we don't have any control over the information it provides. And, for critical life problems, it is important to have authentic information. So, any answer/suggestion provided by this assistant will have citations to the source texts clearly mentioned. This way you can be sure to take all these ideas mentioned from various perspectives and apply them to your life, for your well being.

## **How is this made?**
3 Modern Books(7 Habits of Highly Effective People, Atomic Habits, Ikigai) & 1 Ancient Wisdom Book(Bhagavad Gita) are taken in pdf format and a RAG pipeline is built to answer questions based on the content of these books. More details like the exact tech stack used, architecture, and trade-offs considered are documented separately in `docs`.

### Process followed:
1. Started by defining Product Requirement: [Product Requirements](docs/product_requirement.md)
2. Finalized tech requirements and architecture, considering trade-offs and constraints:
    - [Technical Requirements](docs/technical_requirements.md)
    - [Architecture & Design Decisions](docs/architecture.md)
3. Built a basic version 1 with the tech stack to see a quick working prototype with all the components integrated - backend, frontend, and a basic RAG pipeline.
4. Improved upon the above version by adding semantic chunking, fusion retriever, re-ranking, query decomposition, and tweaking system prompts so as to match the product requirement as close as possible.
5. Implemented evals. Got 80% accuracy, with the current implementation. Analyzed the way forward, to improve the accuracy: [Evaluation Implementation](docs/evals_implementation.md)
6. Added observability and monitoring using Langfuse. (See [Codebase Explanation - Observability](docs/codebase_explanation.md#d-observability-langfuse))
7. As a way forward, I see a bunch of things to do and take this to production and beyond: [Path to Production & Next Steps](docs/next_steps.md)

Detailed engineering standards and development process: [Development Process](docs/development_process.md)

Also, a detailed codebase explanation is available at: [Codebase Explanation](docs/codebase_explanation.md)

## **Notes**:
1. Project is up on - https://modern-sage-three.vercel.app/
   - Used render.io for backend and vercel.com for frontend.
   - You can expect a 50 second delay for the first query, as the backend goes to sleep when not in use.
2. Project is vibe-coded/built using Antigravity, while having complete understanding and precise control over the code at every step.

## 🚀 Quick Start (Local)

**Prerequisites**: Python 3.10+, Node.js 18+.

1.  **Clone & Install**:
    ```bash
    git clone https://github.com/your-repo/modern-sage.git
    cd modern-sage/backend
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create `backend/.env` with your keys:
    ```bash
    OPENAI_API_KEY=sk-...
    PINECONE_API_KEY=pc-...
    COHERE_API_KEY=...       # For Re-ranking
    LANGFUSE_SECRET_KEY=...  # For Observability (Optional)
    ```

3.  **Run Backend**:
    ```bash
    ```bash
    # Run the server from backend directory
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

4.  **Run Frontend**:
    ```bash
    cd ../frontend
    npm install && npm run dev
    ```


