# 09 Product Requirements Document (PRD) - Part 3

**Document Version:** 1.0
**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform

---

## 9. Core Workflows

This section details the step-by-step logic and UI/UX requirements for the core product workflows.

### 9.1 The Authentication & Onboarding Workflow
1.  **Landing Page:** User navigates to `app.codebaseiq.com`. Unauthenticated users are redirected to `/login`.
2.  **OAuth Initiation:** User clicks "Authenticate with GitHub". The frontend redirects to the GitHub OAuth authorization URL, requesting `repo` and `read:org` scopes.
3.  **OAuth Callback:** GitHub redirects back to the backend `/api/auth/callback`. The backend exchanges the code for an access token.
4.  **User Provisioning:**
    *   *If New User:* Backend creates a User record and prompts for Organization Name.
    *   *If Existing User:* Backend retrieves the User record.
5.  **Session Creation:** Backend sets an HTTP-only, Secure cookie containing the JWT.
6.  **Redirection:** User is redirected to `/dashboard`.

### 9.2 The Repository Management Workflow
1.  **Repository List:** On the `/dashboard/repositories` page, the frontend fetches the user's GitHub repositories via the backend.
2.  **State Indication:** Each repository displays a state badge: `Unsynced`, `Queued`, `Indexing`, `Active`, `Failed`.
3.  **Initiating Sync:** User clicks "Connect" on a repository.
4.  **Queueing:** Backend creates a `RepoSyncJob` in PostgreSQL and pushes a task to the Redis Celery queue. The UI state updates to `Queued`.
5.  **Ingestion:** The `ingestion-service` worker picks up the task:
    *   Clones the repo to a temporary volume.
    *   Iterates through files.
    *   Generates AST, Embeddings, and Graph nodes.
    *   Updates the job status in PostgreSQL.
6.  **Completion:** The UI polls (or uses WebSockets) to update the state to `Active`.

### 9.3 The AI Chat Workflow (RAG Pipeline)
1.  **Context Selection:** In the `/chat` UI, the user selects one or more `Active` repositories from a dropdown to set the context scope.
2.  **Query Submission:** User types a question and hits Enter.
3.  **Query Analysis (Backend):**
    *   The `chat-service` analyzes the query to determine intent (e.g., is this a structural question for Neo4j, or a semantic question for Qdrant?).
4.  **Retrieval:**
    *   Generates an embedding of the user's query.
    *   Queries Qdrant for Top-K similar code chunks.
    *   Queries Neo4j for relevant structural dependencies.
5.  **Prompt Assembly:** The backend constructs a massive prompt containing the retrieved code snippets, graph paths, and the user's query, enforcing strict instructions to "only use the provided context."
6.  **Streaming:** The backend sends the prompt to the LLM (e.g., OpenAI API) and streams the chunks back to the Next.js frontend via Server-Sent Events (SSE).
7.  **Rendering:** The frontend renders the Markdown stream, parsing citation tags (e.g., `[src/main.py]`) into clickable links.

### 9.4 The Code Visualization Workflow
1.  **Citation Click:** While reading a chat response, the user clicks a citation link (e.g., `UserController.java`).
2.  **Split Pane Activation:** A side panel slides out from the right (or splits the screen).
3.  **Code Rendering:** The frontend fetches the raw file content from the backend (or GitHub) and renders it using the Monaco Editor component, providing full syntax highlighting.
4.  **Line Highlighting:** The editor automatically scrolls to and highlights the specific line numbers referenced in the citation.

### 9.5 The Notification Workflow
*   **System Notifications:** Non-intrusive toast notifications (bottom right) for events like "Repository Indexing Complete" or "Sync Failed".
*   **Email Notifications:** Triggered via an external service (e.g., SendGrid) for critical events: "Welcome to CodebaseIQ" or "Your Trial is Expiring". Users can toggle email preferences in the Settings panel.
