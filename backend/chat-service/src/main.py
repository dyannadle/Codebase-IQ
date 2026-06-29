from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.application.router import router as chat_router
from src.config.settings import settings

app = FastAPI(
    title="CodebaseIQ Chat Service",
    description="RAG Engine and SSE Streaming endpoint for AI Chat.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat_router)

@app.get("/healthz")
def health_check():
    return {"status": "healthy", "service": "chat-service"}
