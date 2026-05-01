# MindMate Backend System Architecture

Welcome to the **MindMate Backend**, an advanced, AI-driven clinical assessment platform built to provide intelligent mental health screening, diagnosis generation, and specialist matching. 

This repository houses the Python-based backend that orchestrates both the traditional platform logic (users, forums, appointments) and an intricate multi-agent LangGraph pipeline capable of conducting dynamic clinical assessments.

---

##  High-Level System Architecture

The MindMate system is designed around a **modular, multi-tier architecture**:

### 1. The Core API (FastAPI)
At the heart of the application is a high-performance **FastAPI server** (`app.main.py`). It enforces validation using Pydantic, manages cross-origin resource sharing (CORS), and acts as the foundational layer routing all requests. It is divided into several clear domain boundaries:
- **Authentication (`/api/v1/auth`)**: JWT-based session handling, supporting role-based access for Admins, Patients, and Specialists.
- **Platform Endpoints**: Dedicated routes for `/patients`, `/specialists`, `/admins`, `/appointments`, and `/forum`.
- **AI Agent Interface (`/api/v1/agent`)**: Responsible for kicking off the `MindMateState` graph and streaming live AI responses.

### 2. The Agentic Orchestrator (LangGraph Multi-Agent System)
Located in `app/agents/graph.py`, this is the unified **MindMate AI Orchestrator**. It consolidates the Patient Interaction Agent (PIA) and Diagnoser Agent (DA) into one seamless, deterministic LangGraph execution thread.

**Key Nodes & Execution Flow:**
1. **Supervisor Node**: Reads the current transcript and available symptoms, referencing the DSM-5 knowledge base to decide the next clinical module (e.g., ONBOARDING, SCID_SC, MDD, GAD).
2. **Context Manager Node**: Injects dynamic context, temporal data (Pakistan Standard Time constraints), patient demographics, and the designated module system prompt.
3. **LLM Invocation**: Facilitates the empathetic and medically-accurate conversational response.
4. **Symptoms Extractor & Summarizer**: Runs in the background post-LLM call. It evaluates the most recent human/AI turns to extract strict GBNF-validated symptoms and append them to the session state.
5. **Report Generator & Diagnostician**: Once the interaction completes, the graph transitions to the clinical phase. The Diagnostician node structures a detailed medical diagnosis based on accumulated symptoms.
6. **Treatment Planner & Specialist Matcher**: Operates in parallel sequentially after the diagnosis. Generates customized treatment plans and queries the database for approved specialists matching the geographical and differential diagnosis context.

Checkpoints are handled by an async **PostgreSQL Checkpointer**, ensuring conversation persistence and interruptibility per session.

### 3. Service Layer (`app/services/`)
Decouples business logic from HTTP endpoints. 
- **`agent_service.py` & `streaming_service.py`**: Manages secure access to the LangGraph execution, supporting Server-Sent Events (SSE) and streamed JSON chunks.
- **`forum.py`**: A sleek forum engine supporting anonymous posting for patients and restricted, verified-only answers by specialists.
- **`email.py`**: A generic template-driven email service used for sending SMTP notifications for verification, password resets, and appointment bookings.

### 4. Database Layer (PostgreSQL & SQLAlchemy)
The persistence layer utilizes PostgreSQL, driven by asynchronous **SQLAlchemy** and managed schema migrations via **Alembic**.
- **Entities**: Encompasses complex relations for `Patient`, `Specialist`, and `Admin` User Management, alongside domain entities like `ForumQuestion`, `ForumAnswer`, and `Appointment`.
- **Database Migrations**: Changes to `app/models/` are synced securely through Alembic scripts found in the `alembic/` root.

---

## Workflows & Agent Detail

### The Patient Assessment Workflow
1. A Patient requests a new session via the `/agent` endpoint.
2. The agent initializes state and enters the `ONBOARDING` module.
3. As the conversation progresses, the LLM determines whether threshold conditions are met to transition into deeper diagnostic tracks (e.g., assessing MDD vs. Bipolar Risk).
4. Safety first: A specific `RISK` escalation module actively listens for self-harm or severe substance use markers.
5. Finalization produces a fully structured JSON clinical report, a markdown-rendered treatment plan, and a list of 3 matched specialists.

### Forum & Appointment Management
- Patients post completely anonymized queries to seek preliminary answers.
- Only Admins-approved Specialists possess clearance to directly answer these threads, ensuring medical safety in a public forum setting.
- Upon finalizing a treatment plan via the AI orchestrator, patients securely book appointments with recommended specialists using the `appointments` system, which synchronizes database availability and generates Email confirmations.

---

## Setup & Deployment

### Prerequisites
- Python 3.10+
- PostgreSQL Server up and running
- **UV** Package Manager (Optional but recommended, replacing `pip`)

### Local Environment Setup
1. **Clone the repository and install dependencies**:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r pyproject.toml
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root with PostgreSQL connection strings, JWT Secret Keys, LLM Configurations, and Mail server details.
   ```env
   DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/mindmate"
   SECRET_KEY="..."
   # LLM Config
   OPENAI_API_KEY="..." # Or Local Llama.cpp Host
   ```

3. **Run Database Migrations**:
   Ensure all tables apply cleanly via Alembic:
   ```bash
   alembic upgrade head
   ```

4. **Boot up the Server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Verifying System Health
You can verify the entire setup by pinging the heartbeat endpoint: `GET http://localhost:8000/health`.

---
*Built securely for clinical-grade mental health assistance.*
