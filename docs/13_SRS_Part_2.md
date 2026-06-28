# 13 Software Requirements Specification (SRS) - Part 2

**Document Version:** 1.0
**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform

---

## 3. Complete Non-Functional Requirements (NFRs)

The following requirements define system attributes such as performance, reliability, scalability, and security.

### 3.1 Performance
*   **NFR-101 (Query Latency):** The 95th percentile (P95) response time for the initial stream chunk of an AI chat query MUST NOT exceed 3 seconds under normal load.
*   **NFR-102 (API Latency):** Core CRUD operations (e.g., fetching repository lists, updating settings) MUST return within 200 milliseconds (P95).
*   **NFR-103 (Ingestion Throughput):** The system MUST be capable of parsing and embedding a repository of 1,000 files (avg 500 lines/file) in under 10 minutes.
*   **NFR-104 (Concurrent Users):** The system architecture MUST support at least 1,000 concurrent active users initiating chat queries without degradation in performance (NFR-101).

### 3.2 Scalability
*   **NFR-201 (Horizontal Scaling):** All microservices (`auth`, `repo`, `chat`, `vector`, `graph`) MUST be stateless to allow for horizontal scaling via Kubernetes HPA (Horizontal Pod Autoscaler).
*   **NFR-202 (Database Scaling):** PostgreSQL MUST be configured with read replicas. Heavy analytical queries MUST be routed to replicas to protect the primary instance.
*   **NFR-203 (Vector Search Scaling):** Qdrant MUST be deployed in a distributed cluster mode to handle horizontal scaling of the embedding search index across billions of vectors.

### 3.3 Reliability & Availability
*   **NFR-301 (Uptime):** The system MUST achieve 99.9% uptime (excluding scheduled maintenance windows).
*   **NFR-302 (Fault Tolerance):** Failure of the background ingestion worker MUST NOT impact the availability of the web interface or the chat engine for previously indexed repositories.
*   **NFR-303 (Data Durability):** All relational data in PostgreSQL MUST be backed up daily with Point-in-Time Recovery (PITR) enabled.

### 3.4 Security
*   **NFR-401 (Encryption at Rest):** All data stored in PostgreSQL, Qdrant, and Neo4j MUST be encrypted at rest using AES-256.
*   **NFR-402 (Encryption in Transit):** All external and inter-service communication MUST be encrypted using TLS 1.2 or higher.
*   **NFR-403 (Multi-Tenancy Isolation):** Row-Level Security (RLS) MUST be implemented in PostgreSQL to ensure strict data isolation between Organizations. Qdrant and Neo4j queries MUST enforce explicit tenant ID filtering.
*   **NFR-404 (Secret Management):** Application secrets (API keys, DB credentials) MUST NOT be stored in environment variables; they MUST be injected at runtime via a secure secrets manager (e.g., AWS Secrets Manager or HashiCorp Vault).

### 3.5 Maintainability
*   **NFR-501 (Code Quality):** All backend Python code MUST achieve a >85% test coverage and pass `flake8` and `mypy` strict type-checking before merging.
*   **NFR-502 (API Standards):** All REST APIs MUST adhere to OpenAPI 3.1 specifications and provide a live Swagger/ReDoc UI for developer reference.

---

## 4. Business Logic Rules

The system must enforce specific logic rules during the execution of business processes.

*   **BL-001 (Subscription Limits):** If an Organization reaches its maximum allowed active repositories based on its tier (e.g., 10 for Team Tier), the `Sync Repository` button MUST be disabled, and an upgrade prompt MUST be shown.
*   **BL-002 (Re-indexing Trigger):** The system will only re-index a repository if a webhook is received indicating a push to the default branch (e.g., `main` or `master`). Changes on feature branches are ignored to save compute costs.
*   **BL-003 (Orphaned Data Cleanup):** When a user's GitHub OAuth token is detected as invalid/revoked, the system MUST pause all active syncs for that user and flag their account for re-authentication. It MUST NOT delete data automatically unless the Organization is deleted.
*   **BL-004 (Context Window Overflow):** If a user asks a question that requires more retrieved context than the LLM can handle (e.g., "Summarize all 5,000 files"), the business logic MUST intervene, summarize the retrieved vectors via an intermediate LLM call, and pass the summarized context to the final prompt, rather than hard-failing.
