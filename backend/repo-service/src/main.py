from fastapi import FastAPI
from src.application.router import router as repo_router
from src.infrastructure.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CodebaseIQ Repo Service",
    description="Microservice for orchestrating repository ingestion and AST parsing.",
    version="1.0.0"
)

# Include Routers
app.include_router(repo_router)

@app.get("/healthz")
def health_check():
    return {"status": "healthy", "service": "repo-service"}
