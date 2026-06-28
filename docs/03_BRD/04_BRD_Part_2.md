# 04 Business Requirements Document (BRD) - Part 2

**Document Version:** 1.0
**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform

---

## 6. Business Rules

The following core business rules dictate the operation, authorization, and constraints of the CodebaseIQ platform.

### 6.1 Authentication & Authorization
*   **BR-001:** All users must authenticate via a centralized Identity Provider (IdP). For the MVP, GitHub OAuth is mandatory. Future iterations must support SAML SSO (Okta, Azure AD).
*   **BR-002:** Access to a repository's intelligence (chat, graphs, embeddings) is strictly governed by the user's underlying permissions in the source version control system (e.g., GitHub). If a user loses read access to the repo in GitHub, their access in CodebaseIQ must be immediately revoked.
*   **BR-003:** Only users with 'Admin' privileges within the CodebaseIQ Organization can add new billing methods or invite external guests.

### 6.2 Data Ingestion & Retention
*   **BR-004:** The system will only ingest source code files up to a maximum size of 5MB per file. Binaries, media assets (images, videos), and compiled artifacts (`.jar`, `.exe`, `node_modules`) are strictly excluded from AST parsing and embedding.
*   **BR-005:** Upon repository deletion by an Organization Admin, all associated data (source code clones, embeddings in Qdrant, graph nodes in Neo4j) must be hard-deleted from all databases within 24 hours to comply with GDPR/CCPA.

### 6.3 Usage & Throttling
*   **BR-006:** A single Organization's concurrent AI Chat queries are throttled based on their subscription tier to prevent noisy-neighbor performance degradation.
*   **BR-007:** Re-indexing of a repository (updating embeddings and graphs) is triggered via GitHub Webhooks on the `main` branch. Rate limits apply to re-indexing to prevent abuse from highly active monorepos.

---

## 7. Business Constraints

*   **BC-001 (Security):** The application must never store plain-text GitHub Personal Access Tokens (PATs). All credentials must be encrypted at rest using AES-256 and managed via a secure vault (e.g., AWS KMS or HashiCorp Vault).
*   **BC-002 (Compliance):** The platform architecture must support data residency requirements (e.g., EU customers must have their code and embeddings stored exclusively in EU-based data centers).
*   **BC-003 (Performance):** The initial synchronization and embedding of a standard enterprise repository (up to 1,000 files) must complete in under 15 minutes to ensure an acceptable Time-To-Value.
*   **BC-004 (Technology):** The backend services must be written in Python (FastAPI) to natively leverage the Python AI/ML ecosystem (LangChain, tree-sitter wrappers) without relying on heavy IPC bridges.

---

## 8. Revenue Model

CodebaseIQ operates on a B2B SaaS subscription model, designed to capture value from both mid-market agencies and large enterprise engineering departments.

### 8.1 Core Subscription Metrics
Revenue is driven by two primary axes:
1.  **Seat Count:** The number of active developer/user accounts within the Organization.
2.  **Repository Volume:** The total lines of code (LOC) or gigabytes of source code indexed across the Organization.

### 8.2 Additional Revenue Streams
*   **Dedicated Compute (Add-on):** For highly security-conscious enterprises, we offer a dedicated, single-tenant deployment (VPC peering) for an additional premium.
*   **Custom Integrations:** Professional services for integrating CodebaseIQ with legacy, on-premise version control systems (e.g., ancient SVN or Perforce servers).

---

## 9. Pricing Strategy

The pricing is tiered to reduce friction for initial adoption while capturing maximum value from large-scale enterprise deployments.

### 9.1 Team Tier (Self-Serve)
*   **Target:** Startups and small engineering teams (up to 20 developers).
*   **Price:** $49 per user / month.
*   **Limits:** Up to 10 repositories. Shared infrastructure. Standard support.

### 9.2 Enterprise Tier (Sales-Led)
*   **Target:** Mid-market and large enterprises (50+ developers).
*   **Price:** $99 per user / month (volume discounts apply for 500+ seats).
*   **Features:** Unlimited repositories, Advanced RBAC, SAML SSO, Priority SLAs, SOC2 compliance reporting.

### 9.3 On-Premise / VPC Tier (Custom)
*   **Target:** Highly regulated industries (Banking, Healthcare, Defense).
*   **Price:** Custom Annual Contract (Starting at $150,000/year).
*   **Features:** Full data isolation, deployment within the client's own AWS/GCP infrastructure, offline LLM support (no data leaves the client's network).

---

## 10. Risk Assessment

| Risk Category | Description | Probability | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **Security Risk** | Exposure of client source code due to a database breach or misconfigured tenant isolation. | Low | Critical | Implement strict multi-tenant Row-Level Security (RLS) in PostgreSQL. Separate Qdrant collections per tenant. Undergo independent penetration testing before GA. |
| **Technology Risk** | AI Hallucinations providing incorrect architectural advice, leading to developers pushing bad code. | Medium | High | Rely strictly on Graph-Enhanced RAG. If the answer is not in the Neo4j/Qdrant index, the AI is programmed to explicitly state "I don't know" rather than guess. |
| **Market Risk** | Competitors (GitHub Copilot, Cursor) pivot to macro-repository intelligence, absorbing our unique value proposition. | High | High | Move faster to build the Knowledge Graph moat. Copilot focuses on the IDE; CodebaseIQ focuses on the control plane. Deepen integrations with CI/CD pipelines. |
| **Operational Risk** | High LLM inference costs (OpenAI API fees) erode profit margins at scale. | Medium | Medium | Architect the system to be model-agnostic. Route simple queries to cheaper, faster models (e.g., Llama 3) and only use expensive models (GPT-4) for complex reasoning tasks. |

---

## 11. SWOT Analysis

### 11.1 Strengths
*   **Tri-Modal Code Parsing:** Combining AST, Vector Embeddings, and Knowledge Graphs creates an unparalleled understanding of code architecture compared to standard vector-only RAG.
*   **Language Agnostic:** `tree-sitter` allows rapid scaling to support any programming language.
*   **Enterprise Focus:** Built from day one with RBAC, audit logs, and compliance in mind, unlike consumer-focused AI coding tools.

### 11.2 Weaknesses
*   **Cold Start Problem:** The system provides zero value until a repository is fully cloned, parsed, and embedded, which takes time.
*   **Compute Intensive:** Maintaining real-time graphs and embeddings for highly active enterprise repositories requires significant background computing power.

### 11.3 Opportunities
*   **Automated Refactoring:** Moving beyond answering questions to autonomously generating massive PRs to upgrade frameworks across thousands of files.
*   **Security Auditing:** Partnering with SecOps to become the standard tool for identifying deep, multi-service vulnerabilities.

### 11.4 Threats
*   **Platform Lock-in by Tech Giants:** GitHub/Microsoft or Atlassian could build similar features natively into their platform ecosystems.
*   **Data Privacy Backlash:** Enterprises may be hesitant to grant an external SaaS platform read access to their proprietary core intellectual property.
