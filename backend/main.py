from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os
import uvicorn
from llama_index.core.llms import ChatMessage, MessageRole
from rag_engine import get_chat_engine

load_dotenv()

app = FastAPI(title="The Modern Sage API")

# Configure CORS (Allow Requests from Next.js Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with frontend URL (e.g., http://localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.get("/")
def read_root():
    return {"message": "Welcome to The Modern Sage API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/chat")
async def chat_handler(request: ChatRequest):
    try:
        # Initialize chat engine (Note: For production, we might want to cache the index connection)
        chat_engine = get_chat_engine()
        
        # Parse last message as the user query
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
            
        last_message = request.messages[-1]
        if last_message.role != 'user':
             raise HTTPException(status_code=400, detail="Last message must be from user")
        
        user_query = last_message.content

        # Convert previous messages to LlamaIndex ChatMessage history
        # (Skip the last one as it's the current query)
        chat_history = []
        for msg in request.messages[:-1]:
            role = MessageRole.USER if msg.role == 'user' else MessageRole.ASSISTANT
            chat_history.append(ChatMessage(role=role, content=msg.content))

        # Stream the response
        response = chat_engine.stream_chat(user_query, chat_history=chat_history)
        
        # Generator function to yield text chunks
        def event_generator():
            try:
                for token in response.response_gen:
                    # Vercel AI SDK Data Stream Protocol: 0:{json_string_token}\n
                    import json
                    yield f"0:{json.dumps(token)}\n"
            except Exception as e:
                print(f"Streaming error: {e}")

        return StreamingResponse(event_generator(), media_type="text/plain; charset=utf-8")

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
