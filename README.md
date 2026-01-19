# MindMate - AI-Powered Mental Health Platform

**MindMate** is a next-generation mental health platform that leverages advanced AI agents to provide preliminary psychological assessments, symptom recognition, and specialist matching. Built with a privacy-first approach, it bridges the gap between patients and mental health professionals through intelligent automation and empathetic AI interaction.

---

## Key Features

*   **AI Therapist Agent**: A compassionate conversational AI capable of conducting structured clinical interviews (SCID-5 aligned) to understand patient distress.
*   **Real-time Symptom Recognition**: An integrated **Symptom Recognition Agent (SRA)** that analyzes conversations in real-time to extract clinical symptoms and risk factors.
*   **Automated Diagnosis Support**: A **Diagnosis Agent** that uses decision trees and clinical guidelines to suggest differential diagnoses to human specialists.
*   **Smart Booking System**: Seamlessly matches patients with the right specialists based on their assessment profile and availability.
*   **Secure & Compliance-Ready**: Built with role-based access control (RBAC), JWT authentication, and encrypted data storage.

---

## System Architecture

MindMate V2 is built on a modern, microservices-inspired architecture:

### **Backend (FastAPI + LangGraph)**
The core intelligence resides in the Python-based backend, utilizing:
*   **FastAPI**: High-performance async API framework.
*   **LangGraph Orchestrator**: Manages the stateful interactions between multiple AI agents.
*   **PostgreSQL**: Relational database for persistent storage (Users, Appointments, Assessments).
*   **Redis**: High-speed caching for session state and real-time chat context.
*   **SQLAlchemy**: ORM for database interactions.

### **Frontend (React + Vite)**
A sleek, responsive user interface built with:
*   **React 18**: Component-based UI library.
*   **Vite**: Next-generation frontend tooling.
*   **Zustand**: Lightweight state management for auth and sessions.
*   **Framer Motion**: Smooth, modern animations.
*   **TailwindCSS / Custom CSS**: "Glassmorphism" design system.

---

## Core Agentic Systems

MindMate's "brain" is a sophisticated multi-agent system orchestrated by LangGraph, designed to mimic the clinical reasoning of a human practitioner.

### 1. Orchestrator (The Conductor)
*   **Role**: Central nervous system managing the conversation lifecycle.
*   **Logic**:
    *   **Parallel Execution**: Routes user messages to the **Therapist** (Sync) and **SRA** (Async) simultaneously to ensure sub-second latency.
    *   **State Management**: Maintains the global "Session State" (Phase, Risk Level, Symptom Store) in Redis.
    *   **Dynamic Routing**: Triggers the **Diagnosis Agent** only when sufficient diagnostic data has been gathered.

### 2. Therapist Agent V2 (The Interface)
*   **Role**: Conducting the clinical interview with empathy and precision.
*   **Key Capabilities**:
    *   **SCID-5 Guided**: Uses a "Constraint-Based" approach to inject mandatory clinical questions (from the SCID-5 module) naturally into the conversation.
    *   **Deterministic Safety**: Priority override mechanism that scans for self-harm keywords (`risk_level: HIGH/CRITICAL`) before any LLM generation to ensure immediate, safe responses.
    *   **Phase Awareness**: Transitions the session through 4 distinct phases: *Rapport* → *Exploration* → *Deepening* → *Closing*.
*   **Tools**:
    *   `get_guided_question`: Fetches the next clinically required question.
    *   `detect_risk`: Heuristic analysis for crisis detection.

### 3. SRA (Symptom Recognition Agent)
*   **Role**: The silent observer running in the background.
*   **Logic**:
    *   **Async Extraction**: Processes every user message locally to extract clinical entities (e.g., "Insomnia", "Anhedonia").
    *   **Standardization**: Maps raw text to standardized DSM-5 symptom codes and severity scores (0.0 - 1.0).
    *   **Database Sync**: Continuously updates the `symptoms` table in PostgreSQL without blocking the chat.

### 4. Diagnosis Agent V2 (The Clinician)
*   **Role**: Generating differential diagnoses based on accumulated evidence.
*   **Algorithm**: Implements a 3-Step Decision Tree:
    1.  **Screening**: `screen_disorder_categories` aggregates symptoms to identify top potential categories (e.g., Depressive vs. Anxiety).
    2.  **Evaluation**: `evaluate_disorder_criteria` scores specific disorders (e.g., MDD, GAD) against DSM-5 criteria, checking for Core vs. Supporting symptoms.
    3.  **Reporting**: `generate_clinical_report` synthesizes findings into a professional clinical note for the specialist.

---

## Workflows

### **1. The Assessment Flow**
1.  **Start**: Patient initiates a chat session.
2.  **Rapport**: Therapist Agent builds trust and gathers history.
3.  **Extraction**: SRA listens and tags symptoms asynchronously.
4.  **Analysis**: Once sufficient data is gathered, the Diagnosis Agent computes potential conditions.
5.  **Completion**: The session concludes with a summary and a recommendation to book a specialist.

### **2. The Booking Flow**
1.  **Search**: Patients view specialists matched to their specific needs.
2.  **Select**: Choose a provider and view their "Glass Card" profile.
3.  **Book**: Select a time slot (cached via Redis for performance).
4.  **Confirm**: Real-time confirmation and appointment management.

---

## Setup & Installation

### Prerequisites
*   Docker & Docker Compose
*   Node.js v18+ & npm
*   Python 3.11+ & Poetry

### Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/hammadmunir959/MindMate.git
cd MindMate

# 2. Start Backend & Database
cd backend
docker-compose up -d --build

# 3. Start Frontend
cd ../frontend
npm install
npm run dev
```

The application will be available at:
*   **Frontend**: `http://localhost:5173`
*   **Backend API**: `http://localhost:8000/docs`

---

## Testing

We employ a comprehensive testing strategy:
*   **Unit Tests**: `pytest` for backend logic.
*   **Agent Benchmarks**: Specialized scripts to verify agent reasoning and safety.
*   **End-to-End Verification**: `verify_api_contracts.py` ensures seamless frontend-backend integration.

---

