import os
import tempfile
import subprocess
from celery import shared_task
from sqlalchemy.orm import Session
from src.infrastructure.database import SessionLocal
from src.domain.models import Repository, SyncJob, SyncStatus
from src.domain.parser import PythonASTParser
from datetime import datetime, timezone

@shared_task(bind=True, max_retries=3)
def process_repository_sync(self, repository_id: str, job_id: str):
    """
    Main Celery task that orchestrates the ingestion pipeline:
    1. Clone repo
    2. Parse AST
    3. Generate Embeddings (Mocked for this phase)
    """
    db: Session = SessionLocal()
    try:
        repo = db.query(Repository).filter(Repository.id == repository_id).first()
        job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
        
        if not repo or not job:
            return "Repository or Job not found"
            
        # 1. Update Status to CLONING
        _update_status(db, repo, job, SyncStatus.CLONING)
        
        # Clone repo to a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            _clone_repo(repo.clone_url, temp_dir)
            
            # 2. Update Status to PARSING
            _update_status(db, repo, job, SyncStatus.PARSING)
            chunks = _parse_repo(temp_dir)
            
            # 3. Update Status to EMBEDDING
            _update_status(db, repo, job, SyncStatus.EMBEDDING)
            _embed_and_store(chunks, str(repo.organization_id), repository_id)
            
        # 4. Success
        _update_status(db, repo, job, SyncStatus.ACTIVE)
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        return f"Successfully synced repo {repo.full_name} with {len(chunks)} chunks."

    except Exception as e:
        if job and repo:
            _update_status(db, repo, job, SyncStatus.FAILED)
            job.error_logs = str(e)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()

def _update_status(db: Session, repo: Repository, job: SyncJob, status: SyncStatus):
    repo.sync_status = status
    job.status = status
    db.commit()

def _clone_repo(clone_url: str, dest_dir: str):
    # Shallow clone for speed, since we only need the latest code state
    result = subprocess.run(
        ["git", "clone", "--depth", "1", clone_url, dest_dir],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Git clone failed: {result.stderr}")

def _parse_repo(repo_dir: str) -> list:
    parser = PythonASTParser()
    all_chunks = []
    
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    chunks = parser.parse_file(filepath)
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"Failed to parse {filepath}: {e}")
                    
    return all_chunks

def _embed_and_store(chunks: list, org_id: str, repo_id: str):
    """
    MOCK: This will eventually call the litellm embedding API and push to Qdrant.
    For Phase 3, we just simulate the delay and log the payload structure.
    """
    import time
    time.sleep(2) # Simulate network IO to LLM and Vector DB
    print(f"Mocked storing {len(chunks)} chunks in Qdrant for Org {org_id}.")
