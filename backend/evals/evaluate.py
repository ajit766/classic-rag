
import os
import sys
import asyncio
import pandas as pd
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    DatasetGenerator,
)
from llama_index.llms.openai import OpenAI

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from app.services.rag_engine import get_chat_service

async def run_evals():
    print("--- Starting RAG Evaluation ---")
    
    if not settings.PINECONE_API_KEY:
         raise ValueError("PINECONE_API_KEY not found in settings")

    # 1. Setup Infrastructure
    # 1. Setup Infrastructure
    print("1. Connecting to Index...")
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    pinecone_index = pc.Index(settings.INDEX_NAME)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    
    # Initialize Embedding Model explicitly
    from llama_index.embeddings.openai import OpenAIEmbedding
    import llama_index.core
    
    embed_model = OpenAIEmbedding(api_key=settings.OPENAI_API_KEY)
    # Set global settings to avoid default init errors
    llama_index.core.Settings.embed_model = embed_model
    llama_index.core.Settings.llm = OpenAI(model="gpt-4o", api_key=settings.OPENAI_API_KEY)

    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)
    
    # Init Evaluators (GPT-4 as Judge)
    eval_llm = OpenAI(model="gpt-4o", api_key=settings.OPENAI_API_KEY)
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
    
    # Get Chat Engine from Service
    chat_service = get_chat_service()
    chat_engine = chat_service.get_chat_engine()
    
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
    
    # Save to CSV in results directory
    output_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "eval_results.csv")
    
    df.to_csv(output_path, index=False)
    print(f"\nResults saved to '{output_path}'")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_evals())
