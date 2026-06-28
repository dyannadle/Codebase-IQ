import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from src.infrastructure.database import Base

class SyncStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    CLONING = "CLONING"
    PARSING = "PARSING"
    EMBEDDING = "EMBEDDING"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(UUID(as_uuid=True), index=True, nullable=False) # Extracted from JWT
    github_repo_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    clone_url = Column(String, nullable=False)
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.QUEUED, nullable=False)
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    sync_jobs = relationship("SyncJob", back_populates="repository", cascade="all, delete-orphan")

class SyncJob(Base):
    __tablename__ = "sync_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    repository_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=False)
    status = Column(Enum(SyncStatus), default=SyncStatus.QUEUED, nullable=False)
    error_logs = Column(String, nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    repository = relationship("Repository", back_populates="sync_jobs")
