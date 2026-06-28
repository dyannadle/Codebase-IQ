# 17 Low-Level Design (LLD)

**Document Version:** 1.0
**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform

---

## 1. Application Architecture (FastAPI Template)

Every Python backend microservice will adhere to a strict Clean Architecture pattern.

### 1.1 Folder Structure Standard
```text
src/
├── domain/            # Enterprise logic, Entities, Interfaces (No framework dependencies)
├── application/       # Use Cases, Business Logic (Depends on Domain)
├── infrastructure/    # Concrete implementations (DBs, External APIs, FastAPI)
│   ├── database/
│   ├── external/
│   └── web/           # FastAPI routers, dependencies, middleware
├── config/            # Pydantic BaseSettings
└── main.py            # Entry point, dependency injection wiring
```

### 1.2 Design Patterns
*   **Dependency Injection (DI):** Uses FastAPI's `Depends` for request-scoped injection and a custom container (e.g., `punq` or `dependency-injector`) for global service injection.
*   **Repository Pattern:** Abstracts database operations (PostgreSQL, Neo4j, Qdrant) behind interfaces defined in the `domain` layer.
*   **Unit of Work (UoW):** Manages database transactions across multiple repository calls to ensure atomic commits or rollbacks.

---

## 2. Module: `ingestion-service` (The Worker)

The most complex subsystem is the background worker responsible for AST parsing and embedding.

### 2.1 Responsibilities
*   Listen to Redis queue for `RepoSyncJob`.
*   Clone Git repository.
*   Traverse file system.
*   Extract AST using `tree-sitter`.
*   Generate Embeddings and Upsert to Qdrant.
*   Build Knowledge Graph in Neo4j.

### 2.2 Core Classes & Interfaces

```python
# domain/interfaces.py
from typing import Protocol, List

class IGitProvider(Protocol):
    def clone(self, repo_url: str, dest_path: str, token: str) -> bool: ...

class IASTParser(Protocol):
    def parse_file(self, file_path: str, lang: str) -> List['ASTNode']: ...

class IVectorDB(Protocol):
    def upsert_chunks(self, chunks: List['CodeChunk']) -> None: ...

class IGraphDB(Protocol):
    def create_relationship(self, source: str, target: str, rel_type: str) -> None: ...
```

### 2.3 Algorithm: Semantic Code Chunking (Pseudocode)

```python
def chunk_source_file(file_path: str, ast_tree: ASTNode) -> List[CodeChunk]:
    """
    Splits a file semantically based on AST nodes rather than arbitrary text length.
    """
    chunks = []
    
    # 1. Extract Global/Module level imports and variables
    module_header = extract_imports_and_globals(ast_tree)
    
    # 2. Iterate through Class definitions
    for class_node in ast_tree.find_nodes("class_definition"):
        # For huge classes, chunk by method
        if class_node.byte_size > MAX_CHUNK_SIZE:
            for method_node in class_node.find_nodes("method_definition"):
                chunk_text = f"{module_header}\n{class_node.signature}\n{method_node.text}"
                chunks.append(CodeChunk(text=chunk_text, type="method", metadata=...))
        else:
            # Fit entire class in one chunk
            chunk_text = f"{module_header}\n{class_node.text}"
            chunks.append(CodeChunk(text=chunk_text, type="class", metadata=...))
            
    # 3. Handle standalone functions
    for func_node in ast_tree.find_nodes("function_definition"):
         chunk_text = f"{module_header}\n{func_node.text}"
         chunks.append(CodeChunk(text=chunk_text, type="function", metadata=...))
         
    return chunks
```

### 2.4 Exception Handling
*   `GitCloneError`: Raised if OAuth token is revoked or repo is inaccessible. Catches and updates PostgreSQL Job status to `Failed_Auth`.
*   `TreeSitterParseError`: Logged as a warning. The worker falls back to generic line-based chunking for that specific file.
*   `VectorUpsertError`: Triggers an automatic Celery task retry with exponential backoff.

---

## 3. Module: `chat-service` (The RAG Engine)

### 3.1 Responsibilities
*   Accept streaming chat requests.
*   Embed the user query.
*   Retrieve context from Qdrant and Neo4j.
*   Assemble prompt and stream LLM response.

### 3.2 Prompt Assembly (Business Logic)
The `PromptBuilder` class enforces context boundaries.

```python
class PromptBuilder:
    def __init__(self, max_tokens: int = 100000):
        self.max_tokens = max_tokens
        
    def assemble(self, query: str, vector_context: List[CodeChunk], graph_context: List[GraphPath]) -> str:
        system_instructions = "You are an AI architect. Use ONLY the provided context."
        
        # Format Graph Context
        graph_text = "Dependency Paths:\n"
        for path in graph_context:
            graph_text += f"{path.source} -> {path.relationship} -> {path.target}\n"
            
        # Format Vector Context (Prioritized by similarity score)
        vector_text = "Source Code Extracts:\n"
        current_tokens = count_tokens(system_instructions + graph_text)
        
        for chunk in sorted(vector_context, key=lambda x: x.score, reverse=True):
            chunk_tokens = count_tokens(chunk.text)
            if current_tokens + chunk_tokens > self.max_tokens:
                break # Hard cutoff to prevent LLM context overflow
            vector_text += f"--- [{chunk.file_path}:L{chunk.start_line}] ---\n{chunk.text}\n"
            current_tokens += chunk_tokens
            
        return f"{system_instructions}\n\n{graph_text}\n\n{vector_text}\n\nUser Query: {query}"
```

### 3.3 Unit Testing Strategy
*   **Domain & Application Layers:** 100% test coverage using `pytest`. Mocks are used for all `I<Interface>` protocols.
*   **Vector Search Tests:** Mock the LLM embedding generation and assert that the retrieval logic correctly requests `Top-K` from the mocked `IVectorDB`.
*   **Prompt Assembly Tests:** Assert that the prompt never exceeds `max_tokens` when provided with massive mock context arrays.
