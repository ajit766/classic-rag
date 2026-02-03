# Next Steps & Beyond

As next steps:

1.  **Improving Accuracy**: I would aim to improve the evaluation efficiency to 100%. I want to ensure we have better defined product expectations to deliver high accuracy.
2.  **Corner Cases**: There are a few corner cases. For example, if I ask something unrelated, the current output says "This is out of scope" but still tries to retrieve and show results. To fix this, we can add an **LLM Router** to check if the query is within the domain before proceeding with the RAG pipeline.
3.  **Guardrails**: I don't think extensive guardrails are needed for this requirement yet, as we are not deploying this for a company. Since we are using OpenAI (which has good built-in guardrails) and are not using private data, the current setup is specific enough.
4.  **Infrastructure**: Render itself works fine until we reach a scale where we need to look at cost vs. security. It solves the purpose for now.
5.  **At Scale**: Many other things can be considered, like **Caching** the queries for faster results and to reduce repeat work.

