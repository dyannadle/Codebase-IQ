from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.infrastructure.database import get_db
from src.domain.models import Repository, SyncJob, SyncStatus
from src.application.worker import process_repository_sync
import uuid

router = APIRouter(prefix="/repositories", tags=["Repositories"])

@router.post("/{repository_id}/sync")
def trigger_sync(repository_id: str, db: Session = Depends(get_db)):
    """Triggers an asynchronous repository sync job via Celery."""
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    if repo.sync_status in [SyncStatus.QUEUED, SyncStatus.CLONING, SyncStatus.PARSING, SyncStatus.EMBEDDING]:
        raise HTTPException(status_code=400, detail="Sync already in progress")

    # Create SyncJob record
    job = SyncJob(repository_id=repo.id, status=SyncStatus.QUEUED)
    repo.sync_status = SyncStatus.QUEUED
    db.add(job)
    db.commit()
    db.refresh(job)

    # Dispatch to Celery Worker
    process_repository_sync.delay(str(repo.id), str(job.id))
    
    return {"message": "Sync queued", "job_id": str(job.id)}

@router.get("/{repository_id}/status")
def get_sync_status(repository_id: str, db: Session = Depends(get_db)):
    """Gets the current sync status of a repository."""
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    return {
        "repository_id": str(repo.id),
        "status": repo.sync_status.value,
        "last_synced_at": repo.last_synced_at
    }
