# 12 Software Requirements Specification (SRS) - Part 1

**Document Version:** 1.0
**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform
**Standard:** IEEE 830-1998 (Incorporating ISO/IEC/IEEE 29148 concepts)

---

## 1. System Overview

CodebaseIQ is a distributed, microservices-based SaaS platform designed to ingest, analyze, and render intelligent querying capabilities over enterprise software repositories. The system connects to version control platforms (initially GitHub), clones the source code, and processes it through a multi-modal ingestion pipeline. This pipeline generates Abstract Syntax Trees (ASTs) via `tree-sitter`, semantic text chunks, high-dimensional vector embeddings, and a relational knowledge graph. End-users interact with this indexed data via a highly responsive web interface utilizing a Graph-Enhanced Retrieval-Augmented Generation (RAG) architecture.

---

## 2. Complete Functional Requirements

The following requirements define the functional capabilities of the system. Each requirement is assigned a unique identifier (FR-XXX) for traceability.

### 2.1 Authentication & Authorization
*   **FR-101 (GitHub OAuth):** The system MUST allow users to authenticate using GitHub OAuth 2.0.
*   **FR-102 (JWT Session):** Upon successful OAuth login, the `auth-service` MUST issue an HTTP-only, secure JSON Web Token (JWT) with a predefined expiration (e.g., 24 hours).
*   **FR-103 (RBAC):** The system MUST support Role-Based Access Control within an Organization with three predefined roles: `Owner`, `Admin`, and `Member`.
*   **FR-104 (Role Enforcement):** The `api-gateway` MUST validate the JWT and enforce RBAC rules on all API endpoints before routing traffic to downstream microservices.
*   **FR-105 (Session Revocation):** The system MUST provide an endpoint to invalidate a user's session (logout) by blacklisting the active JWT in Redis.

### 2.2 Repository Management
*   **FR-201 (List Repositories):** The system MUST retrieve and display a paginated list of all repositories the authenticated user has access to via the GitHub API.
*   **FR-202 (Sync Initiation):** A user with `Admin` or `Owner` privileges MUST be able to initiate the synchronization of a selected repository.
*   **FR-203 (Sync Status):** The system MUST expose an endpoint to poll (or subscribe via WebSocket) to the current sync status (`Queued`, `Cloning`, `Parsing`, `Embedding`, `Active`, `Failed`).
*   **FR-204 (Repo Deletion):** An `Admin` MUST be able to delete a repository from CodebaseIQ. The system MUST cascade this deletion to PostgreSQL, Qdrant (vectors), and Neo4j (graph nodes).

### 2.3 Repository Indexing Pipeline (Ingestion)
*   **FR-301 (Cloning):** The `repo-service` MUST securely clone the target repository from GitHub into an ephemeral, isolated container volume.
*   **FR-302 (File Filtering):** The pipeline MUST explicitly ignore files listed in `.gitignore`, binary files (images, compiled artifacts), and files exceeding the 5MB size limit.
*   **FR-303 (AST Parsing):** The pipeline MUST process supported languages (Python, Java, TS/JS) through `tree-sitter` to generate an Abstract Syntax Tree.
*   **FR-304 (Relationship Extraction):** The pipeline MUST identify imports, function calls, and class inheritances from the AST and queue these for graph insertion.

### 2.4 Embedding Generation & Vector Search
*   **FR-401 (Semantic Chunking):** The pipeline MUST split source code files into semantic chunks (e.g., separating distinct classes or functions) rather than arbitrary character lengths.
*   **FR-402 (Vectorization):** The `vector-service` MUST pass the semantic chunks to the configured LLM API (e.g., OpenAI `text-embedding-3-small`) to generate embeddings.
*   **FR-403 (Qdrant Storage):** The system MUST store generated embeddings in Qdrant, tagging each vector with metadata including `organization_id`, `repo_id`, `file_path`, and `chunk_index`.
*   **FR-404 (Vector Retrieval):** The system MUST perform a Cosine Similarity search against Qdrant based on a user's embedded query, returning the Top-K most relevant chunks within 500ms.

### 2.5 Knowledge Graph
*   **FR-501 (Node Creation):** The `graph-service` MUST create nodes in Neo4j representing Files, Classes, Functions, and External Libraries.
*   **FR-502 (Edge Creation):** The `graph-service` MUST create directed edges representing relationships (e.g., `CALLS`, `IMPORTS`, `IMPLEMENTS`).
*   **FR-503 (Graph Querying):** The system MUST be able to execute Cypher queries against Neo4j to trace the execution path from a source function to all downstream dependencies.

### 2.6 Chat Engine (RAG)
*   **FR-601 (Prompt Assembly):** The `chat-service` MUST construct a system prompt that injects the Top-K vector results and relevant Neo4j graph paths.
*   **FR-602 (Streaming Response):** The `chat-service` MUST stream the LLM response back to the client via Server-Sent Events (SSE).
*   **FR-603 (Citation Injection):** The LLM response MUST include structured citation tags mapping back to the specific source files provided in the context.
*   **FR-604 (Context Window Enforcement):** The system MUST automatically prune the injected context if it exceeds the target LLM's maximum context window (e.g., 128k tokens).

### 2.7 Automated Diagram Generation
*   **FR-701 (Dependency Visualization):** The system MUST provide an endpoint to generate a Mermaid.js diagram representing the microservice or class-level dependencies of a selected repository.
*   **FR-702 (UI Rendering):** The frontend MUST render valid Mermaid syntax directly in the chat interface or a dedicated visualization canvas.
