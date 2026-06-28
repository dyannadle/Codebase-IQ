# Security Documentation

**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform  
**Document Number:** SEC-001  
**Version:** 1.0.0  
**Date:** June 2026  
**Confidentiality:** Internal / Restricted  

---

## Document Control

### Version History
| Version | Date | Author | Description of Changes |
| :--- | :--- | :--- | :--- |
| 0.9.0 | 2026-06-15 | Security Architect | Initial Draft |
| 1.0.0 | 2026-06-28 | Security Team | Final Approval for V1.0 Release |

### Table of Contents
1.  Introduction
2.  Threat Model
3.  OWASP ASVS Alignment
4.  Authentication & Authorization
5.  Secrets Management & Encryption
6.  SOC2 & GDPR Readiness
7.  Incident Response
8.  Glossary

---

## 1. Introduction
This document outlines the comprehensive security architecture and operational security practices for the CodebaseIQ platform. It serves as the definitive reference for engineering teams, compliance auditors, and prospective enterprise clients.

## 2. Threat Model
CodebaseIQ utilizes the STRIDE methodology for threat modeling.

### 2.1 Identified Threats & Mitigations
*   **Spoofing:** An attacker attempts to impersonate an organization admin. *Mitigation:* GitHub OAuth enforcing 2FA + HTTP-Only, Secure JWT cookies.
*   **Tampering:** An attacker modifies vector embeddings to poison the RAG context. *Mitigation:* All internal APIs (Vector Service) require mTLS authentication. External access is firewalled.
*   **Repudiation:** A user claims they did not delete a repository. *Mitigation:* Immutable Audit Logs stored in PostgreSQL.
*   **Information Disclosure:** Tenant A accesses Tenant B's source code. *Mitigation:* PostgreSQL Row-Level Security (RLS) and strict payload filtering in Qdrant.
*   **Denial of Service:** Massive chat queries exhaust LLM API limits. *Mitigation:* Token Bucket rate limiting at the API Gateway via Redis.
*   **Elevation of Privilege:** A Member escalates to Admin. *Mitigation:* RBAC roles are cryptographically signed in the JWT and verified at every API gateway route.

## 3. OWASP ASVS Alignment
CodebaseIQ aims for **OWASP Application Security Verification Standard (ASVS) Level 2**, suitable for applications handling sensitive B2B data (source code).

*   **V2 (Authentication):** Passwords are not managed locally (delegated to GitHub).
*   **V3 (Session Management):** JWTs have a max lifespan of 12 hours. Refresh tokens are rotated on use.
*   **V14 (Configuration):** Security Headers (HSTS, CSP, X-Frame-Options) are strictly enforced by the API Gateway.

## 4. Authentication & Authorization

### 4.1 Authentication (OAuth & JWT)
CodebaseIQ operates as a GitHub OAuth App. Upon successful OAuth callback, the `auth-service` issues an asymmetric JWT (RS256).
*   **Issuer:** `auth.codebaseiq.com`
*   **Audience:** `api.codebaseiq.com`
*   **Storage:** Stored in the browser as an `HttpOnly`, `Secure`, `SameSite=Strict` cookie to prevent XSS exfiltration.

### 4.2 Role-Based Access Control (RBAC)
Authorization is enforced via RBAC middleware at the FastAPI router level.
*   `Owner`: Full billing and deletion rights.
*   `Admin`: Can manage users and force repository syncs.
*   `Member`: Read-only access to Chat and Dashboards.

## 5. Secrets Management & Encryption

### 5.1 Secrets Management
Hardcoded secrets are strictly prohibited. The platform utilizes **HashiCorp Vault** (or AWS Secrets Manager) for:
*   GitHub OAuth Client Secrets
*   LLM Provider API Keys (OpenAI, Stripe)
*   Database Credentials (PostgreSQL, Neo4j, Qdrant)

### 5.2 Encryption (Data at Rest & Transit)
*   **Transit:** TLS 1.3 enforced for all external traffic. Internal cluster traffic uses mTLS via Istio service mesh.
*   **At Rest:** PostgreSQL EBS volumes, Qdrant disks, and Redis instances are encrypted using AES-256 via the Cloud Provider's Key Management Service (KMS).

## 6. SOC2 & GDPR Readiness

### 6.1 SOC2 Type II Readiness
*   **Security:** Covered by encryption and access controls.
*   **Availability:** Multi-AZ deployment and Disaster Recovery plans.
*   **Confidentiality:** Strict RLS to prevent cross-tenant data leakage.

### 6.2 GDPR Considerations
*   **Right to be Forgotten:** The `DELETE /api/organizations/{id}` endpoint executes a cascading hard-delete across PostgreSQL, Qdrant, and Neo4j, completely wiping all user and repository data within minutes.

## 7. Incident Response
*   **Severity 1 (Critical):** Data breach or complete platform outage. PagerDuty alerts entire engineering leadership. Target Resolution: < 4 hours.
*   **Severity 2 (High):** Core feature broken (e.g., Sync failing for all users). Target Resolution: < 12 hours.

## 8. Glossary
*   **mTLS (Mutual TLS):** Two-way authentication between microservices.
*   **RLS (Row-Level Security):** Database feature to restrict data access based on user context.
*   **STRIDE:** Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege.
