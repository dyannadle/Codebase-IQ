# 20 AI Architecture

**Document Version:** 1.0
**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform

---

## 1. Executive Summary of AI Architecture

CodebaseIQ's AI Architecture is a sophisticated, multi-modal **Graph-Enhanced Retrieval-Augmented Generation (RAG)** pipeline. It moves beyond naïve vector similarity search by combining Abstract Syntax Tree (AST) parsing, dense vector embeddings, and Neo4j Knowledge Graph traversal. This architecture ensures responses are structurally accurate, deterministic, and highly resistant to hallucination.

---

## 2. Model Abstraction & Architecture

The system utilizes an **LLM Gateway Pattern** to remain model-agnostic, preventing vendor lock-in and allowing dynamic routing based on task complexity and cost.

*   **Embedding Model:** `text-embedding-3-small` (OpenAI) or equivalent open-source dense models (e.g., `bge-large-en`) optimized for code retrieval.
*   **Routing/Fast LLM:** `Llama-3-8b` or `gpt-4o-mini` for intent classification, query rewriting, and simple summarization tasks to minimize latency and cost.
*   **Reasoning LLM:** `gpt-4o` or `claude-3.5-sonnet` strictly reserved for the final RAG generation step where deep reasoning over massive code contexts is required.
*   **Abstraction Layer:** All LLM calls route through `litellm` or a similar abstraction library, exposing a unified API regardless of the underlying provider.

---

## 3. The Ingestion Pipeline

### 3.1 AST Parsing (`tree-sitter`)
Before any text is embedded, the raw source code is parsed using `tree-sitter`. This allows the system to understand the precise grammatical structure of the code (functions, classes, imports, parameters) rather than treating it as a flat string.

### 3.2 Semantic Chunking Strategy
Naïve text chunking (e.g., splitting every 500 tokens) breaks code logic. CodebaseIQ uses **AST-Aware Chunking**:
1.  **Module Header Chunk:** Extracts file-level imports and global variables. This chunk is prepended to all subsequent chunks from the same file to preserve context.
2.  **Function/Class Chunks:** The AST parser extracts entire functions or classes as discrete chunks.
3.  **Fallback Chunking:** If a class exceeds the maximum chunk token limit (e.g., 2000 tokens), it is recursively split at the method level.

### 3.3 Embedding Pipeline
1.  The AST chunks are passed to the Embedding Model.
2.  The resulting high-dimensional vectors are stored in **Qdrant**.
3.  **Metadata Injection:** Every vector is tagged with `repo_id`, `file_path`, `chunk_type` (e.g., `class_def`), and `start_line` for precise filtering.

### 3.4 Knowledge Graph Construction
While embeddings capture semantic meaning, the **Neo4j Knowledge Graph** captures execution flow.
*   The AST parser identifies that `FileA` imports `FunctionB`.
*   A Cypher query inserts: `(FileA)-[:IMPORTS]->(FunctionB)`.
*   This allows the system to deterministically answer "What files will break if I modify FunctionB?" without relying on probabilistic LLM guessing.

---

## 4. The Retrieval Pipeline (RAG)

### 4.1 Query Intent & Rewriting
User queries are often ambiguous (e.g., "How does auth work?").
*   The Routing LLM rewrites the query into a highly optimized search string.
*   The Intent Analyzer determines if the query requires purely Semantic context, purely Structural context, or Hybrid context.

### 4.2 Context Retrieval
CodebaseIQ utilizes **Hybrid Retrieval**:
1.  **Dense Retrieval (Qdrant):** Performs Cosine Similarity search to find chunks semantically related to the rewritten query.
2.  **Graph Retrieval (Neo4j):** Executes Cypher queries to retrieve the 1-hop and 2-hop dependency neighbors of the files identified in the dense retrieval step.

### 4.3 Ranking & Re-ranking
1.  The combined results from Qdrant and Neo4j often exceed the target context window.
2.  A lightweight cross-encoder (Re-ranker) re-scores the retrieved chunks based on their explicit relevance to the specific user query, filtering out "noisy" semantic matches.

---

## 5. Prompt Engineering & Generation

### 5.1 Prompt Assembly
The final prompt sent to the Reasoning LLM is highly structured to enforce guardrails.

```text
[SYSTEM]
You are an expert Software Architect analyzing the user's repository.
You MUST base your answer EXCLUSIVELY on the provided <CONTEXT>.
If the <CONTEXT> does not contain the answer, you MUST state: "I cannot determine this from the current context."
Do NOT guess or use external knowledge.
Cite your sources using the format: [file_path:line_number].

[GRAPH CONTEXT]
<Neo4j Path Data>

[CODE CONTEXT]
<Ranked Qdrant Chunks>

[USER QUERY]
<Original User Request>
```

### 5.2 Token Optimization & Caching
*   **Semantic Caching:** If a user asks "How does login work?" and another user in the same repo asks "Explain the login flow", a semantic cache (e.g., Redis + Vector Search) returns the previously generated response immediately, bypassing the Retrieval and Generation phases entirely.
*   **Context Window Management:** The Prompt Assembler dynamically counts tokens (using `tiktoken`) and strictly truncates the lowest-ranked context chunks to ensure the prompt never exceeds the provider's token limit.

---

## 6. Guardrails & Hallucination Reduction

*   **Zero-Hallucination Mandate:** The strict prompt instructions (Section 5.1) are the primary defense against hallucination.
*   **Citation Validation:** A post-generation parsing step verifies that every citation `[file:line]` generated by the LLM actually exists in the provided context. If the LLM invents a file, the response is flagged or retried.
*   **Temperature:** The Generation LLM is set to a highly deterministic temperature (`T=0.1`) to favor factual extraction over creative prose.

---

## 7. Performance & Latency Optimization

*   **Streaming (SSE):** To combat the high TTFB (Time to First Byte) of Reasoning LLMs processing massive contexts, responses are streamed token-by-token via Server-Sent Events.
*   **Parallel Retrieval:** Qdrant similarity searches and Neo4j Cypher queries are executed asynchronously in parallel.

---

## 8. Memory Management

*   **Conversational Memory:** The chat interface maintains a sliding window of the last N conversation turns (e.g., last 5 messages). This short-term memory is injected into the Prompt Assembly phase to handle follow-up questions like "Can you explain the third step in more detail?".

---

## 9. Evaluation Metrics (LLMOps)

CodebaseIQ's AI performance is continuously evaluated using the RAGAS framework (Retrieval Augmented Generation Assessment):
*   **Faithfulness:** Does the generated answer strictly rely on the retrieved context? (Measures Hallucination).
*   **Answer Relevance:** Does the answer directly address the user's query?
*   **Context Precision:** Were the highly ranked retrieved chunks actually relevant? (Evaluates the Re-ranker).
*   **Context Recall:** Did the retrieval system find all the necessary information to answer the question? (Evaluates Qdrant/Neo4j).

---

## 10. Future AI Roadmap

*   **Agentic Workflows (LangGraph):** Moving from passive RAG to active Agents. E.g., An Agent that can execute `git grep` or run unit tests in a sandbox to verify its own answers before showing them to the user.
*   **Multi-Modal Architecture:** Allowing users to upload a whiteboard photo of a system architecture, which the LLM then compares against the actual Neo4j Graph to identify discrepancies.
*   **Autonomous Pull Requests:** Utilizing the LLM not just to read code, but to generate and submit PRs for framework upgrades or security patches based on the retrieved context.
