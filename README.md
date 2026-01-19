# MindMate - AI-Powered Mental Health Platform

**MindMate** is a next-generation mental health platform that leverages advanced AI agents to provide preliminary psychological assessments, symptom recognition, and specialist matching. Built with a privacy-first approach, it bridges the gap between patients and mental health professionals through intelligent automation and empathetic AI interaction.

---

## 🚀 Key Features

*   **🤖 AI Therapist Agent**: A compassionate conversational AI capable of conducting structured clinical interviews (SCID-5 aligned) to understand patient distress.
*   **🧠 Real-time Symptom Recognition**: An integrated **Symptom Recognition Agent (SRA)** that analyzes conversations in real-time to extract clinical symptoms and risk factors.
*   **🩺 Automated Diagnosis Support**: A **Diagnosis Agent** that uses decision trees and clinical guidelines to suggest differential diagnoses to human specialists.
*   **📅 Smart Booking System**: Seamlessly matches patients with the right specialists based on their assessment profile and availability.
*   **🛡️ Secure & Compliance-Ready**: Built with role-based access control (RBAC), JWT authentication, and encrypted data storage.

---

## 🏗️ System Architecture

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

## 🤖 Core Agentic Systems

MindMate's "brain" consists of four specialized agents working in harmony:

### 1. Orchestrator Agent
*   **Role**: The conductor of the system.
*   **Function**: Routes user messages to the appropriate sub-agent, manages session phases (Rapport -> Assessment -> Safety Check -> Conclusion), and maintains global context.

### 2. Therapist Agent
*   **Role**: The front-facing conversationalist.
*   **Function**: Engages the user in natural dialogue. It uses **Semantic Router** to detect intent and **SCID-5** banks to ask clinically relevant questions without sounding robotic.

### 3. SRA (Symptom Recognition Agent)
*   **Role**: The analytical observer.
*   **Function**: Runs in the background, analyzing user inputs to extract entities like "Insomnia", "Anxiety", or "Suicidal Ideation". It maps these to standardized clinical codes.

### 4. Diagnosis Agent
*   **Role**: The clinical synthesizer.
*   **Function**: Aggregates extracted symptoms and runs them through clinical decision trees (implemented as MCP Tools) to generate a preliminary clinical report and differential diagnoses.

---

## 🔄 Workflows

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

## 🛠️ Setup & Installation

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

## 🧪 Testing

We employ a comprehensive testing strategy:
*   **Unit Tests**: `pytest` for backend logic.
*   **Agent Benchmarks**: Specialized scripts to verify agent reasoning and safety.
*   **End-to-End Verification**: `verify_api_contracts.py` ensures seamless frontend-backend integration.

---

## 📄 License
Private Project - CodeKonix AI Labs.
