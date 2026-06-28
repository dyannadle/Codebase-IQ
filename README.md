# CodebaseIQ - Repository Intelligence Platform

CodebaseIQ is an enterprise-grade AI platform that ingests your GitHub repositories, parses the code into an Abstract Syntax Tree (AST), generates a structural Knowledge Graph, and provides a conversational RAG (Retrieval-Augmented Generation) interface to answer complex architectural questions.

## System Architecture
* **Frontend:** Next.js (React) with a premium dark-mode developer UI.
* **Backend:** Microservices architecture using Python (FastAPI).
    * `auth-service`: Handles GitHub OAuth and JWT issuance.
    * `repo-service`: Orchestrates Celery workers to clone and parse repositories via `tree-sitter`.
    * `chat-service`: The Hybrid RAG engine streaming LLM responses.
* **Databases:** PostgreSQL (Relational), Redis (Message Broker), Qdrant (Vector DB), Neo4j (Graph DB).

---

## 🚀 How to Run the Platform Locally

To run the entire platform, you will need to open **multiple terminal tabs** to run the services side-by-side.

### Prerequisites
* Docker Desktop installed and running.
* Python 3.12+ installed.
* Node.js installed.

### Step 1: Start the Infrastructure
Open a terminal in the root of the project and start the Docker containers:
```powershell
cd "d:\Projects\Codebase IQ"
docker-compose up -d
```
*(This starts PostgreSQL, Redis, Qdrant, and Neo4j in the background).*

### Step 2: Install Backend Dependencies
Open a terminal, create the virtual environment, and install the Python packages:
```powershell
cd "d:\Projects\Codebase IQ\backend"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

### Step 3: Start the Microservices
**⚠️ CRITICAL:** You must run **EACH** of the following commands in a **BRAND NEW terminal tab**, and you **MUST activate the virtual environment** in every single tab before starting the service.

#### Terminal Tab 1: Auth Service (Gateway)
```powershell
cd "d:\Projects\Codebase IQ\backend"
.\venv\Scripts\activate
cd auth-service
uvicorn src.main:app --reload --port 8000
```
*(Ensure `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are set in `backend/auth-service/.env`)*

#### Terminal Tab 2: Repo Ingestion Service
```powershell
cd "d:\Projects\Codebase IQ\backend"
.\venv\Scripts\activate
cd repo-service
uvicorn src.main:app --reload --port 8001
```

#### Terminal Tab 3: Celery Background Worker
```powershell
cd "d:\Projects\Codebase IQ\backend"
.\venv\Scripts\activate
cd repo-service
celery -A src.config.celery_app worker --loglevel=info
```

#### Terminal Tab 4: Chat Engine (RAG)
```powershell
cd "d:\Projects\Codebase IQ\backend"
.\venv\Scripts\activate
cd chat-service
uvicorn src.main:app --reload --port 8002
```
*(Ensure `OPENAI_API_KEY` is set in `backend/chat-service/.env`)*

---

### Step 4: Start the Frontend
Finally, open one more terminal tab to run the Next.js web client:
```powershell
cd "d:\Projects\Codebase IQ\web-client"
npm install
npm run dev
```

The UI will be accessible at **http://localhost:3000**.
