# QA Documentation

**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform  
**Document Number:** QA-001  
**Version:** 1.0.0  
**Date:** June 2026  
**Confidentiality:** Internal / Restricted  

---

## Document Control

### Version History
| Version | Date | Author | Description of Changes |
| :--- | :--- | :--- | :--- |
| 0.9.0 | 2026-06-22 | QA Lead | Initial Test Strategy Draft |
| 1.0.0 | 2026-06-28 | Engineering Team | Final QA Plan Approval |

### Table of Contents
1.  Test Strategy & Automation
2.  Test Types (Regression, Smoke, Sanity)
3.  Performance & Security Testing
4.  Traceability Matrix & Test Cases
5.  Bug Workflow & Release Checklist

---

## 1. Test Strategy & Automation
The CodebaseIQ QA strategy relies heavily on the "Test Pyramid," pushing maximum coverage to the Unit and Integration layers to enable rapid CI/CD deployments.

### 1.1 Automation Strategy
*   **Unit Tests (Backend):** `pytest` handles all Python microservices. Minimum 85% coverage required. Mocks are used for Qdrant and Neo4j connections.
*   **Unit Tests (Frontend):** `Jest` and `React Testing Library` for Next.js components.
*   **API Tests:** `Postman`/`Newman` collections run in CI/CD against ephemeral staging environments.
*   **End-to-End (E2E) UI Tests:** `Playwright` is used to automate core user journeys (e.g., GitHub Login -> Sync Repo -> Ask Chat Question).

### 1.2 Manual Testing
Manual testing is strictly reserved for exploratory testing, UI/UX polish (CSS rendering on obscure browsers), and evaluating the subjective *quality* of the AI's RAG responses.

## 2. Test Types

### 2.1 Smoke Testing
A fast (< 2 minute) subset of E2E tests run immediately after deployment to production to verify core functionality:
1.  Can a user log in?
2.  Does the `/healthz` endpoint return 200 OK?
3.  Can a test user send a generic chat query and receive a 200 OK stream?

### 2.2 Regression & Sanity Testing
*   **Regression:** The full Playwright and API test suites are executed on every PR to `main` to ensure new features do not break existing logic.
*   **Sanity:** Focused testing on a specific microservice after a targeted bug fix (e.g., testing only the `tree-sitter` parser after a parser bug is resolved).

## 3. Performance & Security Testing

### 3.1 Performance Testing
*   **Load Testing:** `k6` is used to simulate 1,000 concurrent users sending chat requests to the API Gateway to ensure the Redis rate-limiter and Kubernetes HPAs function correctly.
*   **Vector DB Latency:** Automated benchmark tests run nightly to ensure Qdrant Cosine Similarity search remains < 500ms even when loaded with 10M+ vectors.

### 3.2 Security Testing
*   **SAST:** `Bandit` and `SonarQube` run on every commit.
*   **DAST:** OWASP ZAP runs weekly against the staging environment.
*   **Penetration Testing:** A third-party security firm will conduct manual pentesting 30 days prior to General Availability (GA).

## 4. Traceability Matrix & Test Cases

| Req ID | Requirement Description | Test Case ID | Test Type | Status |
| :--- | :--- | :--- | :--- | :--- |
| FR-101 | GitHub OAuth Login | TC-AUTH-01 | E2E (Playwright) | Draft |
| FR-202 | Sync Repository | TC-REPO-05 | API (Newman) | Draft |
| FR-402 | Generate Embeddings | TC-AI-12 | Unit (Pytest) | Draft |

### 4.1 Sample Test Case: TC-AUTH-01
*   **Title:** Verify successful GitHub OAuth Login.
*   **Precondition:** User is not authenticated.
*   **Steps:** 
    1. Navigate to `/login`. 
    2. Click "Continue with GitHub". 
    3. Enter valid GitHub credentials in the mock provider.
*   **Expected Result:** User is redirected to `/dashboard` and a valid JWT is present in cookies.

## 5. Bug Workflow & Release Checklist

### 5.1 Bug Workflow (Jira)
1.  **New:** Reported by User/QA.
2.  **Triage:** Product Manager assigns priority (P0-P4) and targets a sprint.
3.  **In Progress:** Developer claims the ticket.
4.  **In Review:** PR submitted, automated tests run.
5.  **In QA:** Deployed to staging, QA verifies.
6.  **Closed:** Verified and deployed to Production.

### 5.2 Release Checklist
*   [ ] All P0 and P1 bugs resolved.
*   [ ] CI/CD pipeline green (100% pass rate).
*   [ ] Penetration test remediations applied.
*   [ ] Runbook updated with any new infrastructure changes.
*   [ ] Marketing collateral approved.
