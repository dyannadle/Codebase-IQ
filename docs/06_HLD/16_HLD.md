# 16 High-Level Design (HLD)

**Document Version:** 1.0
**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform

---

## 1. Introduction

This High-Level Design document outlines the macro-architecture of CodebaseIQ using the C4 Model (Context, Container, Component) and provides detailed data flow and pipeline architectures. The system is designed as a cloud-native, microservices-oriented platform deployed via Docker and Kubernetes.

---

## 2. C4 Model Diagrams

### 2.1 Context Diagram (Level 1)
This diagram illustrates how external actors interact with the CodebaseIQ system.

```mermaid
C4Context
    title System Context diagram for CodebaseIQ

    Person(developer, "Software Developer", "A developer seeking to understand repository architecture.")
    Person(admin, "Organization Admin", "Manages users, billing, and repositories.")

    System(codebaseiq, "CodebaseIQ Platform", "AI-powered repository intelligence system.")

    System_Ext(github, "GitHub", "External VCS provider for authentication and source code.")
    System_Ext(llm, "LLM Provider", "External AI API (e.g., OpenAI) for embeddings and generation.")
    System_Ext(stripe, "Stripe", "External payment gateway for subscription billing.")

    Rel(developer, codebaseiq, "Asks questions, views architecture diagrams", "HTTPS")
    Rel(admin, codebaseiq, "Manages syncs, billing, users", "HTTPS")

    Rel(codebaseiq, github, "Authenticates users, clones repositories", "HTTPS/Git")
    Rel(codebaseiq, llm, "Generates embeddings and RAG completions", "HTTPS")
    Rel(codebaseiq, stripe, "Manages subscriptions and webhooks", "HTTPS")
```

### 2.2 Container Diagram (Level 2)
This diagram zooms into the CodebaseIQ System to show the high-level containers (Microservices and Databases).

```mermaid
C4Container
    title Container diagram for CodebaseIQ

    Person(user, "User", "Developer or Admin")

    Container(web_app, "Web Application", "Next.js, TypeScript", "Delivers the SPA for chat and dashboard.")
    Container(api_gateway, "API Gateway", "FastAPI, Nginx", "Routes requests, handles JWT validation and rate limiting.")
    
    Container(auth_svc, "Auth Service", "FastAPI, Python", "Handles OAuth, RBAC, and sessions.")
    Container(repo_svc, "Repo Service", "FastAPI, Python", "Manages GitHub webhooks and ingestion queues.")
    Container(chat_svc, "Chat Service", "FastAPI, Python", "Executes the RAG pipeline and streams responses.")
    Container(ingestion_worker, "Ingestion Worker", "Celery, Python", "Background worker for AST parsing and embedding.")

    ContainerDb(postgres, "PostgreSQL", "PostgreSQL", "Stores user profiles, organizations, RBAC, and job states.")
    ContainerDb(redis, "Redis", "Redis", "Message broker for Celery and caching layer.")
    ContainerDb(qdrant, "Qdrant", "Vector Database", "Stores high-dimensional code chunk embeddings.")
    ContainerDb(neo4j, "Neo4j", "Graph Database", "Stores the repository structural knowledge graph.")

    Rel(user, web_app, "Visits app.codebaseiq.com", "HTTPS")
    Rel(web_app, api_gateway, "Makes API calls", "JSON/HTTPS")
    
    Rel(api_gateway, auth_svc, "Routes /auth requests", "HTTP")
    Rel(api_gateway, repo_svc, "Routes /repos requests", "HTTP")
    Rel(api_gateway, chat_svc, "Routes /chat requests", "HTTP/SSE")

    Rel(auth_svc, postgres, "Reads/Writes user data")
    Rel(repo_svc, postgres, "Reads/Writes repo metadata")
    Rel(repo_svc, redis, "Pushes tasks to queue")
    
    Rel(ingestion_worker, redis, "Pulls tasks from queue")
    Rel(ingestion_worker, qdrant, "Upserts embeddings")
    Rel(ingestion_worker, neo4j, "Upserts graph nodes/edges")
    Rel(ingestion_worker, postgres, "Updates job status")

    Rel(chat_svc, qdrant, "Queries for semantic context")
    Rel(chat_svc, neo4j, "Queries for structural paths")
```

### 2.3 Component Diagram (Level 3 - Chat Service)
This diagram zooms into the `chat-service` to illustrate its internal components.

```mermaid
C4Component
    title Component diagram for Chat Service

    Container(api_gateway, "API Gateway", "FastAPI", "Incoming requests")
    
    Container_Boundary(chat_svc, "Chat Service") {
        Component(chat_controller, "Chat Controller", "FastAPI Router", "Handles SSE connections and input validation")
        Component(intent_analyzer, "Intent Analyzer", "Python", "Determines if query needs Vector, Graph, or Both")
        Component(vector_client, "Qdrant Client", "Python", "Executes vector similarity search")
        Component(graph_client, "Neo4j Client", "Python", "Executes Cypher path traversal")
        Component(prompt_builder, "Prompt Assembler", "Python", "Constructs the final LLM prompt with context boundaries")
        Component(llm_client, "LLM Streamer", "Python", "Handles external API streaming and token management")
    }
    
    System_Ext(llm, "External LLM", "OpenAI / Gemini")

    Rel(api_gateway, chat_controller, "Sends chat query")
    Rel(chat_controller, intent_analyzer, "Parses intent")
    Rel(intent_analyzer, vector_client, "Triggers vector search")
    Rel(intent_analyzer, graph_client, "Triggers graph search")
    
    Rel(vector_client, prompt_builder, "Returns top-k chunks")
    Rel(graph_client, prompt_builder, "Returns Cypher paths")
    
    Rel(prompt_builder, llm_client, "Passes assembled prompt")
    Rel(llm_client, llm, "Streams completion request")
    Rel(llm_client, chat_controller, "Yields Markdown chunks")
```

---

## 3. Deployment & Infrastructure Diagram

The system is deployed on a managed Kubernetes cluster (EKS/GKE) across multiple availability zones for high availability.

```mermaid
architecture-beta
    group k8s(Cloud: Kubernetes Cluster)
    
    service gateway(API Gateway)
    service web(Next.js Frontend)
    
    group backend(Backend Microservices)
    service auth(Auth Service)
    service repo(Repo Service)
    service chat(Chat Service)
    service worker(Ingestion Worker)
    
    group db(Managed Databases)
    database pg(PostgreSQL RDS)
    database redis(Redis ElastiCache)
    database qdrant(Qdrant Cloud)
    database neo4j(Neo4j AuraDB)
    
    gateway:R --> L:web
    gateway:B --> T:auth
    gateway:B --> T:repo
    gateway:B --> T:chat
    
    repo:R --> L:redis
    worker:L --> R:redis
    
    auth:B --> T:pg
    repo:B --> T:pg
    worker:B --> T:pg
    
    worker:B --> T:qdrant
    worker:B --> T:neo4j
    chat:B --> T:qdrant
    chat:B --> T:neo4j
```

*(Note: The above uses Mermaid experimental architecture syntax. If rendering fails, fallback to a standard graph deployment diagram).*

---

## 4. Repository Processing Pipeline (Data Flow)

The data flow from a raw GitHub repository to actionable intelligence involves several distinct phases.

```mermaid
sequenceDiagram
    participant Github as GitHub
    participant Repo as Repo Service
    participant Redis as Redis Queue
    participant Worker as Ingestion Worker
    participant DB as Postgres/Qdrant/Neo4j

    Repo->>Github: Request Clone URL (OAuth Token)
    Github-->>Repo: Returns URL
    Repo->>Redis: Enqueue Sync Task (repo_id)
    Redis-->>Worker: Consume Task
    Worker->>Worker: git clone (shallow)
    
    loop For each file in repo
        Worker->>Worker: Check .gitignore / > 5MB
        Worker->>Worker: tree-sitter AST parsing
        Worker->>Worker: Extract Functions, Classes, Imports
        Worker->>Worker: Chunk code (Semantic)
        Worker->>DB: Upsert Neo4j Nodes (Files, Classes)
        Worker->>DB: Upsert Neo4j Edges (CALLS, IMPORTS)
        Worker->>LLM API: Request Embedding for Chunks
        LLM API-->>Worker: Return Vector [0.1, 0.4...]
        Worker->>DB: Upsert Qdrant Vector + Metadata
    end
    
    Worker->>DB: Update Task Status -> ACTIVE
```

---

## 5. AI RAG Pipeline (Data Flow)

How the `chat-service` processes a user query.

```mermaid
sequenceDiagram
    participant User
    participant Chat as Chat Service
    participant Qdrant
    participant Neo4j
    participant Prompt as Prompt Assembler
    participant LLM as External LLM

    User->>Chat: "Where is the Stripe webhook handled?"
    Chat->>LLM: Embed Query String
    LLM-->>Chat: Return Query Vector
    
    par Vector Search
        Chat->>Qdrant: Cosine Search (Top 5)
        Qdrant-->>Chat: Returns File A:L40, File B:L10
    and Graph Search
        Chat->>Neo4j: Cypher Query (Find "Stripe" nodes)
        Neo4j-->>Chat: Returns dependency path (Gateway -> PaymentService)
    end
    
    Chat->>Prompt: Assemble(Context, Graph Paths, User Query)
    Prompt-->>Chat: Formatted System Prompt
    
    Chat->>LLM: Stream Completion(Formatted Prompt)
    loop Stream Chunks
        LLM-->>Chat: token chunk
        Chat-->>User: SSE Chunk (Markdown)
    end
```
