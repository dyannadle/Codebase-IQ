# 06 Business Requirements Document (BRD) - Part 4

**Document Version:** 1.0
**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform

---

## 16. Project Scope

### 16.1 In-Scope (MVP & V1.0)
The initial release of CodebaseIQ will include the following core capabilities:
*   Authentication via GitHub OAuth.
*   Multi-tenant Organization workspace management.
*   Integration with GitHub Cloud to list and select repositories.
*   Automated background cloning and indexing pipeline (AST generation, semantic chunking).
*   Vector Database (Qdrant) integration for semantic search.
*   Graph Database (Neo4j) integration to map files, classes, and method calls.
*   AI Chat Interface (Web UI) utilizing a Graph-Enhanced RAG pipeline.
*   Support for the following languages: Python, Java, JavaScript, TypeScript.
*   Basic Role-Based Access Control (Admin vs. Member).
*   Subscription management and billing integration (Stripe).

### 16.2 Out-of-Scope (Deferred to V2.0+)
The following items are explicitly excluded from the initial release to ensure a focused, high-quality MVP:
*   Integration with GitLab, Bitbucket, or on-premise SVN/Perforce servers.
*   Support for C++, Rust, Go, PHP, Kotlin, Swift (planned for future phases).
*   Automated creation of Pull Requests (autonomous refactoring).
*   IDE Plugins (VS Code, IntelliJ) – V1.0 is exclusively a Web Application.
*   SAML SSO (Okta, Azure AD) integration (reserved for Enterprise tier in V2.0).

---

## 17. Budget Estimation

*Assumption: 12-Month Development cycle to V1.0 with a team of 30+ engineers, product managers, and designers.*

*   **Personnel (Engineering, Product, Design, QA):** $6,500,000
*   **Cloud Infrastructure (Dev/Test/Staging environments):** $150,000
*   **LLM API Costs (Development & Initial Beta inference):** $50,000
*   **Security & Compliance (Penetration testing, SOC2 audit prep):** $80,000
*   **Marketing & Go-To-Market (Launch campaign, sales collateral):** $220,000
*   **Contingency (15%):** $1,050,000
*   **Estimated Total Year 1 Budget:** **~$8,050,000**

---

## 18. Timeline & Milestones

| Phase | Milestone | Estimated Duration | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Architecture & Infrastructure | Month 1-2 | Docker Compose setup, CI/CD pipelines, API Gateway routing, Base Microservice templates, Database provisioning. |
| **Phase 2** | Ingestion Engine Core | Month 3-5 | GitHub OAuth, Repo Cloning worker, `tree-sitter` AST parsing, text chunking, pushing embeddings to Qdrant. |
| **Phase 3** | Knowledge Graph & Intelligence | Month 6-8 | Extracting relationships to Neo4j, developing the RAG Prompt pipeline, testing inference latency and accuracy. |
| **Phase 4** | User Experience & Frontend | Month 9-10 | Next.js Web UI, Chat interface, Dashboard, Settings, Billing integration. |
| **Phase 5** | QA, Security & Beta Launch | Month 11-12 | Penetration testing, load testing, onboarding 10 Beta design partners, fixing edge cases. |
| **Phase 6** | General Availability (V1.0) | Month 12 | Public launch, marketing push, opening self-serve registration. |

---

## 19. Governance & Compliance

*   **Security Standard:** The platform will be architected to meet **SOC2 Type II** standards.
*   **Data Privacy:** Compliance with **GDPR** and **CCPA** is mandatory. This includes the ability to hard-delete an organization's data upon request and managing cookie consent.
*   **Code Review Governance:** All internal code commits for CodebaseIQ must require approval from at least two senior engineers and pass automated static analysis (SAST) and dependency vulnerability scanning (SCA) before merging.
*   **Access Control:** Production database access is strictly limited to authorized DevOps personnel via ephemeral, audited credentials (e.g., HashiCorp Vault).

---

## 20. Approval Workflow

The implementation of this Business Requirements Document requires formal sign-off from the following stakeholders before engineering resources are fully allocated:

1.  **Product Management Lead:** Approves the scope, features, and timeline.
2.  **Chief Technology Officer (CTO):** Approves the technical feasibility, architectural constraints, and infrastructure budget.
3.  **Chief Information Security Officer (CISO):** Approves the data handling rules, compliance targets, and security constraints.
4.  **Chief Executive Officer (CEO) / Sponsor:** Final approval of the business case, ROI, and budget allocation.
