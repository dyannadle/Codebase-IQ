# 15 Software Requirements Specification (SRS) - Part 4

**Document Version:** 1.0
**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform

---

## 8. Background Jobs & Caching

### 8.1 Background Processing (Celery/Redis)
*   **JOB-001 (Ingestion Queue):** Repository cloning, AST parsing, and embedding generation are heavily CPU-bound and MUST be executed asynchronously via Celery worker nodes to prevent blocking the API event loop.
*   **JOB-002 (Garbage Collection):** A nightly cron job MUST run to identify and permanently purge soft-deleted repositories and expired JWT sessions from the databases.

### 8.2 Caching Strategy
*   **CAC-001 (API Caching):** The `api-gateway` MUST cache relatively static responses, such as a user's GitHub repository list (which rarely changes), in Redis for 5 minutes to reduce external API rate limiting.
*   **CAC-002 (AST Caching):** The ingestion pipeline SHOULD cache the generated AST of unmodified files across syncs to dramatically speed up re-indexing after a small commit.

## 9. Configuration & Deployment

### 9.1 Configuration Management
*   **CFG-001 (Environment Variables):** All application configuration (DB URLs, API keys, log levels) MUST be injected via Environment Variables conforming to the 12-Factor App methodology.

### 9.2 Deployment Architecture
*   **DEP-001 (Containerization):** All services, including the Next.js frontend, MUST be packaged as Docker images.
*   **DEP-002 (Local Development):** The repository MUST include a comprehensive `docker-compose.yml` that orchestrates all microservices, PostgreSQL, Neo4j, Qdrant, and Redis with a single `docker-compose up` command.
*   **DEP-003 (Production):** The production deployment strategy MUST target Kubernetes (EKS/GKE) using Helm charts, ensuring zero-downtime rolling updates.

## 10. Traceability Matrix

| Feature / Epic | SRS Requirements | Design Module |
| :--- | :--- | :--- |
| **Authentication (Epic 1)** | FR-101, FR-102, FR-103, BL-003 | `auth-service` |
| **Repo Management (Epic 2)** | FR-201, FR-202, FR-301, JOB-001 | `repo-service` |
| **Parsing & Embedding (Epic 2)**| FR-303, FR-401, FR-402, NFR-103 | `ingestion-service` |
| **Knowledge Graph (Epic 3)** | FR-501, FR-502, FR-503 | `graph-service` |
| **RAG Chat (Epic 4)** | FR-601, FR-602, NFR-101, ERR-002 | `chat-service` |
| **Web UI (Epic 4)** | UI-001, UI-002, UI-003 | `web-client` |
| **Security & Auditing (Epic 5)**| FR-104, NFR-401, LOG-003 | `api-gateway`, DBs |

## 11. Glossary

*   **AST (Abstract Syntax Tree):** A tree representation of the abstract syntactic structure of source code, used by CodebaseIQ to understand code syntax without being confused by formatting or comments.
*   **RAG (Retrieval-Augmented Generation):** An AI technique where an LLM is provided with relevant retrieved data (context) before generating an answer, preventing hallucinations.
*   **tree-sitter:** A parser generator tool and incremental parsing library used to build the AST.
*   **Qdrant:** An open-source vector database used for semantic similarity search.
*   **Neo4j:** A native graph database used to store and query the relationships between code entities.
*   **JWT (JSON Web Token):** A compact URL-safe means of representing claims to be transferred between two parties, used for session management.
*   **SSE (Server-Sent Events):** A standard describing how servers can initiate data transmission towards clients once an initial client connection has been established. Used for streaming the AI chat response.
