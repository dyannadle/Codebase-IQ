from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from src.domain.schemas import ChatRequest
from src.application.rag_engine import rag_engine

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/stream")
async def chat_stream(
    request: ChatRequest, 
    authorization: str = Header(...)
):
    """
    Streams a RAG-augmented response back to the client.
    Expects a Bearer JWT in the Authorization header.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
        
    # In a full implementation, we decode the JWT here to extract the organization_id
    # For now, we mock the extracted org_id
    mock_org_id = "org-1234-uuid"
    
    try:
        # Get the async generator from the RAG Engine
        generator = await rag_engine.process_query(
            query=request.query,
            org_id=mock_org_id,
            repo_ids=request.repository_ids
        )
        
        # Return Server-Sent Events (SSE) Stream
        return StreamingResponse(generator, media_type="text/event-stream")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
