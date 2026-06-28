from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.application.router import router as auth_router
from src.infrastructure.database import engine, Base
from src.config.settings import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CodebaseIQ Auth Service",
    description="Microservice for handling GitHub OAuth and issuing JWTs.",
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
app.include_router(auth_router)

@app.get("/healthz")
def health_check():
    return {"status": "healthy", "service": "auth-service"}
