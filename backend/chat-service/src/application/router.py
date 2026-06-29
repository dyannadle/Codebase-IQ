from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from src.domain.schemas import ChatRequest
from src.application.rag_engine import rag_engine
from src.domain.security import get_current_user, TokenData
import uuid

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/stream")
async def chat_stream(
    request: ChatRequest, 
    current_user: TokenData = Depends(get_current_user)
):
    """
    Streams a RAG-augmented response back to the client.
    Expects a Bearer JWT in the Authorization header or cookie.
    """
    # Organization ID is derived from User ID for now
    org_id = current_user.user_id
    
    try:
        # Get the async generator from the RAG Engine
        generator = await rag_engine.process_query(
            query=request.query,
            org_id=org_id,
            repo_ids=request.repository_ids
        )
        
        # Return Server-Sent Events (SSE) Stream
        return StreamingResponse(generator, media_type="text/event-stream")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
