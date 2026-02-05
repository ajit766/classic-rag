
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from llama_index.core.llms import ChatMessage, MessageRole

from app.models.chat import ChatRequest
from app.services.rag_engine import get_chat_service, ChatService
from app.core.logging import logger

router = APIRouter()

@router.post("/chat")
async def chat_handler(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    try:
        # Parse last message as the user query
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
            
        last_message = request.messages[-1]
        if last_message.role != 'user':
             raise HTTPException(status_code=400, detail="Last message must be from user")
        
        user_query = last_message.content

        # Convert previous messages to LlamaIndex ChatMessage history
        chat_history = []
        for msg in request.messages[:-1]:
            role = MessageRole.USER if msg.role == 'user' else MessageRole.ASSISTANT
            chat_history.append(ChatMessage(role=role, content=msg.content))

        logger.info(f"Processing chat request: {user_query[:50]}...")
        
        # Stream the response
        chat_engine = chat_service.get_chat_engine()
        response = chat_engine.stream_chat(user_query, chat_history=chat_history)
        
        # Generator function to yield text chunks
        def event_generator():
            try:
                for token in response.response_gen:
                    # Vercel AI SDK Data Stream Protocol: 0:{json_string_token}\n
                    import json
                    yield f"0:{json.dumps(token)}\n"
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                
        return StreamingResponse(event_generator(), media_type="text/plain; charset=utf-8")

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
