import os
import asyncio
import pandas as pd
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    DatasetGenerator,
)
from llama_index.llms.openai import OpenAI
from rag_engine import get_chat_engine

# Load Env
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE-API-KEY")
INDEX_NAME = "modern-sage"

async def run_evals():
    print("--- Starting RAG Evaluation ---")
    
    # 1. Setup Infrastructure
    print("1. Connecting to Index...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pc.Index(INDEX_NAME)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    
    # Init Evaluators (GPT-4 as Judge)
    eval_llm = OpenAI(model="gpt-4o")
    faithfulness_evaluator = FaithfulnessEvaluator(llm=eval_llm)
    relevancy_evaluator = RelevancyEvaluator(llm=eval_llm)
    
    # 2. Generate Synthetic Dataset (The "Golden" Set)
    print("2. Generating Synthetic Test Questions (This may take a moment)...")
    # We retrieve random nodes to generate questions from
    retriever = index.as_retriever(similarity_top_k=5)
    nodes = retriever.retrieve("context") # Dummy query to fetch random nodes if we don't scan full DB
    # Note: efficient way is to just fetch top-k for a generic query to sample content.
    
    # Create questions
    dataset_generator = DatasetGenerator(
        nodes,
        llm=eval_llm,
        show_progress=True,
        num_questions_per_chunk=1
    )
    eval_questions = await dataset_generator.agenerate_questions_from_nodes(num=5)
    print(f"   Generated {len(eval_questions)} Test Questions.")

    # 3. Run Evaluation Loop
    results = []
    chat_engine = get_chat_engine()
    
    print("3. Running Evaluation Loop...")
    for i, question in enumerate(eval_questions):
        print(f"   [{i+1}/{len(eval_questions)}] Testing: '{question}'")
        
        # Get RAG Response
        response = chat_engine.chat(question)
        
        # Evaluate
        faith_result = faithfulness_evaluator.evaluate_response(response=response)
        relevancy_result = relevancy_evaluator.evaluate_response(query=question, response=response)
        
        results.append({
            "Question": question,
            "Answer": str(response)[:100] + "...", # Truncate for display
            "Faithful": faith_result.passing,
            "Relevant": relevancy_result.passing,
            "Faith_Score": faith_result.score,
            "Rel_Score": relevancy_result.score
        })

    # 4. Report
    df = pd.DataFrame(results)
    
    print("\n--- EVALUATION RESULTS ---")
    print(df[["Question", "Faithful", "Relevant", "Faith_Score"]])
    
    overall_faith = df["Faithful"].mean()
    overall_rel = df["Relevant"].mean()
    
    print("\n--- SUMMARY ---")
    print(f"Faithfulness Rate: {overall_faith:.2%}")
    print(f"Relevancy Rate:    {overall_rel:.2%}")
    
    # Save to CSV
    df.to_csv("eval_results.csv", index=False)
    print("\nResults saved to 'eval_results.csv'")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_evals())
