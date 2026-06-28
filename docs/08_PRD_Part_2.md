# 08 Product Requirements Document (PRD) - Part 2

**Document Version:** 1.0
**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform

---

## 5. User Personas

To ensure the product solves real-world pain points, we focus on three primary user personas:

### 5.1 Persona: "Onboarding Owen" (Junior/Mid Software Engineer)
*   **Demographics:** 24-28 years old, 2 years of experience.
*   **Pain Points:** Overwhelmed by the size of the enterprise monorepo. Afraid to ask "stupid questions" to senior developers. Struggles to find where specific business logic (e.g., pricing calculation) resides.
*   **Primary Use Case:** Uses CodebaseIQ as a safe, omniscient mentor. Asks: "Where is the Stripe webhook handled?" or "Explain how the `UserSession` class is instantiated."
*   **Success Metric:** Reduces time to first merged PR from 4 weeks to 1 week.

### 5.2 Persona: "Architect Alice" (Senior/Staff Engineer)
*   **Demographics:** 35+ years old, 10+ years of experience.
*   **Pain Points:** Spends too much time reviewing PRs that break architectural boundaries. Frustrated by outdated architecture diagrams. Needs to understand the blast radius of deprecating an old API.
*   **Primary Use Case:** Uses CodebaseIQ to visualize dependencies. Asks: "Generate a Mermaid diagram of all services that call the `LegacyAuth` module." or "Which database tables will be affected if I delete `UserController.java`?"
*   **Success Metric:** Reduces time spent manually tracing code dependencies by 80%.

### 5.3 Persona: "Manager Mike" (Engineering Manager / Director)
*   **Demographics:** 40+ years old, manages 3-5 engineering teams.
*   **Pain Points:** Lacks visibility into technical debt. Needs to ensure the team is shipping fast but not accumulating vulnerabilities.
*   **Primary Use Case:** Uses the CodebaseIQ Dashboard. Looks at the "Dead Code Report" and "Architectural Drift" metrics.
*   **Success Metric:** Measurable reduction in reported production bugs and faster team velocity.

---

## 6. User Journeys

### 6.1 Journey 1: The Initial Onboarding (Day 1)
1.  **Trigger:** Mike signs up for CodebaseIQ and creates an Organization.
2.  **Action:** Mike clicks "Connect GitHub" and authorizes the OAuth App.
3.  **Action:** Mike selects 5 core repositories from a list.
4.  **System Action:** CodebaseIQ kicks off background ingestion. A progress bar shows "Parsing AST... Generating Embeddings... Building Graph".
5.  **Resolution:** After 15 minutes, Mike receives an email notification: "Your Repositories are Ready."

### 6.2 Journey 2: The Architectural Query
1.  **Trigger:** Alice needs to refactor the payment gateway but doesn't know all the upstream dependencies.
2.  **Action:** Alice logs in and selects the `payment-service` and `api-gateway` repositories in the Chat Interface.
3.  **Action:** Alice asks: "Show me exactly how a payment intent is created and routed from the gateway to the payment service."
4.  **System Action:** The RAG pipeline queries Neo4j for the call graph and Qdrant for semantic context.
5.  **Resolution:** CodebaseIQ streams a response detailing the 4 steps of the flow, with clickable citations to `PaymentController.ts:L45` and `StripeService.ts:L112`.

---

## 7. Use Cases

*   **UC-01: Explain Code Block:** User highlights a snippet of code and asks for an explanation of its logic and time complexity.
*   **UC-02: Trace Data Flow:** User asks how a specific variable (e.g., `userId`) flows from an API endpoint down to the database layer.
*   **UC-03: Generate Documentation:** User requests a complete `README.md` for a newly ingested, undocumented microservice.
*   **UC-04: Identify Unused Code:** User requests a list of all functions in a repository that are never imported or called by any other file.

---

## 8. User Stories & Acceptance Criteria

### Epic: Identity & Access Management
*   **US-1.1:** As an Engineering Manager, I want to log in using my GitHub account so that I don't have to remember another password.
    *   *AC-1.1.1:* The login page must feature a prominent "Continue with GitHub" button.
    *   *AC-1.1.2:* Upon successful OAuth callback, the system must create a user record in PostgreSQL or retrieve the existing one.
    *   *AC-1.1.3:* The system must issue a secure, HTTP-only JWT for session management.
*   **US-1.2:** As an Admin, I want to invite my team members to my CodebaseIQ Organization.
    *   *AC-1.2.1:* The Admin can enter email addresses to send invites.
    *   *AC-1.2.2:* Invited users are automatically associated with the Admin's Organization upon signup.

### Epic: The Data Ingestion Pipeline
*   **US-2.1:** As a User, I want to select which repositories CodebaseIQ should index.
    *   *AC-2.1.1:* The system must display a paginated list of all repositories the authenticated user has access to on GitHub.
    *   *AC-2.1.2:* The user can toggle a switch to "Sync" a repository.
*   **US-2.2:** As the System, I need to parse the repository into an Abstract Syntax Tree (AST).
    *   *AC-2.2.1:* The background worker must successfully use `tree-sitter` to parse Python and Java files.
    *   *AC-2.2.2:* The parser must ignore binary files, images, and files listed in `.gitignore`.

### Epic: The Intelligence Layer (Chat)
*   **US-3.1:** As a Developer, I want to ask questions in a chat interface and get answers based on my code.
    *   *AC-3.1.1:* The chat UI must support Markdown rendering (for code blocks).
    *   *AC-3.1.2:* The AI's response must stream in real-time (SSE or WebSockets).
    *   *AC-3.1.3:* The AI must include clickable citations that open a split-pane view of the referenced source code file.
