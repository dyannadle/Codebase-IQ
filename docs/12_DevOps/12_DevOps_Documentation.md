# DevOps Documentation

**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform  
**Document Number:** DEV-001  
**Version:** 1.0.0  
**Date:** June 2026  
**Confidentiality:** Internal / Restricted  

---

## Document Control

### Version History
| Version | Date | Author | Description of Changes |
| :--- | :--- | :--- | :--- |
| 0.9.0 | 2026-06-20 | DevOps Lead | Initial Infrastructure Draft |
| 1.0.0 | 2026-06-28 | Engineering Team | Final Architecture Approval |

### Table of Contents
1.  Infrastructure Architecture
2.  Containerization (Docker)
3.  CI/CD Pipeline (GitHub Actions)
4.  Kubernetes Deployment Strategy
5.  Monitoring, Logging, & Tracing
6.  Backup & Disaster Recovery

---

## 1. Infrastructure Architecture
CodebaseIQ utilizes a cloud-native architecture deployed primarily on AWS (or GCP equivalent) using Infrastructure as Code (Terraform).

### 1.1 Infrastructure Diagram (Mermaid)
```mermaid
architecture-beta
    group vpc(AWS VPC - eu-central-1)
    
    group public(Public Subnet)
    service alb(Application Load Balancer)
    
    group private(Private Subnet - EKS Cluster)
    service web(Next.js Pods)
    service api(FastAPI Pods)
    service worker(Celery Worker Pods)
    
    group data(Data Subnet - Managed Services)
    database rds(Amazon RDS PostgreSQL)
    database redis(Amazon ElastiCache Redis)
    database qdrant(Qdrant Managed Cloud)
    database neo4j(Neo4j AuraDB)
    
    alb:B --> T:web
    alb:B --> T:api
    api:B --> T:rds
    api:B --> T:redis
    api:B --> T:qdrant
    api:B --> T:neo4j
    worker:L --> R:redis
```

## 2. Containerization (Docker)
All microservices are containerized using minimal, security-hardened base images (e.g., `python:3.11-slim`, `node:20-alpine`).
*   **Docker Compose:** Used strictly for local development to spin up the entire stack, including local instances of PostgreSQL, Redis, Qdrant, and Neo4j.
*   **Multi-Stage Builds:** Used to ensure production images do not contain build tools or compilers, keeping image sizes < 300MB and reducing the attack surface.

## 3. CI/CD Pipeline (GitHub Actions)
The CI/CD pipeline enforces zero-downtime deployments and strict quality gates.

### 3.1 Continuous Integration (CI)
Triggered on every Pull Request to `main`:
1.  **Linting:** `flake8`, `mypy`, `eslint`.
2.  **Testing:** `pytest` (Backend), `jest` (Frontend). Must maintain >85% coverage.
3.  **Security Scan:** `Trivy` scans Docker images for CVEs. `Bandit` scans Python code for vulnerabilities.

### 3.2 Continuous Deployment (CD)
Triggered on merge to `main`:
1.  Build and tag Docker images with the Git SHA.
2.  Push images to Amazon ECR (Elastic Container Registry).
3.  Apply Terraform state changes.
4.  Update Kubernetes Deployment manifests (via ArgoCD or Helm).

## 4. Kubernetes Deployment Strategy
*   **Blue-Green Deployment:** To ensure zero downtime, ArgoCD orchestrates Blue-Green deployments. Traffic is shifted to the new version only after health checks (`/healthz`) pass.
*   **Auto Scaling (HPA):** The `chat-service` and `ingestion-worker` pods are configured with Horizontal Pod Autoscalers, scaling up based on CPU utilization (> 70%) and Celery queue length.

## 5. Monitoring, Logging, & Tracing

### 5.1 Monitoring
*   **Prometheus & Grafana:** Every FastAPI service exposes `/metrics`. Grafana dashboards track P95 latency, 5xx error rates, and active LLM tokens consumed.

### 5.2 Logging
*   **Structured Logging:** All logs are JSON formatted.
*   **Aggregation:** FluentBit runs as a DaemonSet, forwarding logs to Elasticsearch/Kibana (ELK) or Datadog for centralized querying.

### 5.3 Tracing
*   **OpenTelemetry:** Distributed tracing is implemented across the API Gateway, Chat Service, and LLM APIs to pinpoint latency bottlenecks in the RAG pipeline.

## 6. Backup & Disaster Recovery
*   **PostgreSQL:** AWS RDS Automated Backups with 30-day retention and Point-in-Time Recovery (PITR).
*   **Disaster Recovery (DR):** RTO (Recovery Time Objective) is 4 hours. RPO (Recovery Point Objective) is 15 minutes. Infrastructure can be redeployed to a secondary AWS region using Terraform in < 30 minutes.
