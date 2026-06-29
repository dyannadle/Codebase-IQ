import os
import tempfile
import subprocess
from celery import shared_task
from src.config.celery_app import celery_app
from sqlalchemy.orm import Session
from src.infrastructure.database import SessionLocal
from src.domain.models import Repository, SyncJob, SyncStatus
from src.domain.parser import PythonASTParser
from datetime import datetime, timezone

@celery_app.task(bind=True, max_retries=3)
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
            _embed_and_store(chunks, str(repo.organization_id), repository_id, temp_dir)
            
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

def _embed_and_store(chunks: list, org_id: str, repo_id: str, repo_dir: str):
    """
    Generates embeddings using litellm and stores the chunks in Qdrant,
    and indexes file dependency relationships in Neo4j.
    """
    import litellm
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qdrant_models
    import uuid
    from src.config.settings import settings

    # 1. Generate Embeddings (batch call)
    litellm.api_key = settings.OPENAI_API_KEY
    embeddings = []
    
    # Batch embeddings for performance
    batch_size = 16
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        texts = [chunk["content"] for chunk in batch_chunks]
        
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
            # Fallback mock embedding
            batch_embeddings = [[0.0] * 1536 for _ in range(len(batch_chunks))]
        else:
            try:
                response = litellm.embedding(
                    model="text-embedding-3-small",
                    input=texts
                )
                batch_embeddings = [item["embedding"] for item in response.data]
            except Exception as e:
                print(f"Embedding API error: {e}")
                batch_embeddings = [[0.0] * 1536 for _ in range(len(batch_chunks))]
                
        embeddings.extend(batch_embeddings)

    # 2. Push Chunks to Qdrant
    qdrant_client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)
    collection_name = "codebase_chunks"
    
    if not qdrant_client.collection_exists(collection_name):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=qdrant_models.VectorParams(size=1536, distance=qdrant_models.Distance.COSINE)
        )
        
    # Clear old points for this repository
    qdrant_client.delete(
        collection_name=collection_name,
        points_selector=qdrant_models.FilterSelector(
            filter=qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="repository_id",
                        match=qdrant_models.MatchValue(value=repo_id)
                    )
                ]
            )
        )
    )
    
    # Upsert new points
    points = []
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        relative_path = os.path.relpath(chunk["filepath"], repo_dir).replace("\\", "/")
        point_id = str(uuid.uuid4())
        points.append(
            qdrant_models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "organization_id": org_id,
                    "repository_id": repo_id,
                    "filepath": relative_path,
                    "content": chunk["content"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "type": chunk["type"]
                }
            )
        )
        
    if points:
        qdrant_client.upsert(collection_name=collection_name, points=points)
        print(f"Stored {len(points)} chunks in Qdrant collection '{collection_name}' for Repository {repo_id}.")

    # 3. Resolve Dependencies and Store in Neo4j
    from neo4j import GraphDatabase
    
    # Discover all python files in the directory
    repo_files = []
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith(".py"):
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, repo_dir).replace("\\", "/")
                repo_files.append(rel_path)

    # Parse imports for each file
    parser = PythonASTParser()
    file_dependencies = {}
    for rel_path in repo_files:
        abs_path = os.path.join(repo_dir, rel_path)
        imports = parser.extract_import_modules(abs_path)
        resolved_deps = []
        for imp in imports:
            resolved_file = _resolve_import_to_file(imp, repo_files)
            if resolved_file and resolved_file != rel_path:
                resolved_deps.append(resolved_file)
        file_dependencies[rel_path] = list(set(resolved_deps))

    # Initialize Neo4j driver
    neo4j_driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )
    
    with neo4j_driver.session() as session:
        # Clear existing nodes/relations for this repo
        session.run("MATCH (f:File {repository_id: $repo_id}) DETACH DELETE f", repo_id=repo_id)
        
        # Create all File nodes
        for rel_path in repo_files:
            session.run(
                "CREATE (f:File {path: $path, repository_id: $repo_id})",
                path=rel_path,
                repo_id=repo_id
            )
            
        # Create IMPORTS edges
        for src_path, targets in file_dependencies.items():
            for target_path in targets:
                session.run(
                    """
                    MATCH (src:File {path: $src_path, repository_id: $repo_id})
                    MATCH (dst:File {path: $target_path, repository_id: $repo_id})
                    CREATE (src)-[:IMPORTS]->(dst)
                    """,
                    src_path=src_path,
                    target_path=target_path,
                    repo_id=repo_id
                )
                
    neo4j_driver.close()
    print(f"Indexed {len(repo_files)} files and their dependencies in Neo4j for Repository {repo_id}.")

def _resolve_import_to_file(imported_module: str, repo_files: list[str]) -> str | None:
    parts = imported_module.split(".")
    suffix = "/".join(parts)
    for f in repo_files:
        if f.endswith(suffix + ".py") or f.endswith(suffix + "/__init__.py"):
            return f
    return None
