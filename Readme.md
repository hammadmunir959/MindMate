# MindMate

## Overview

MindMate is composed of backend and frontend services that collaborate to power AI-driven mental health assessments and related workflows. This repository contains the core application logic, adapters, utilities, and shared templates required to orchestrate these assessments.

## Repository Layout

- `backend/` – FastAPI-based services, domain logic, and agent orchestration.
- `frontend/` – Web client for delivering assessment experiences (if present).
- `infrastructure/` – Infrastructure-as-code definitions, deployment scripts, or DevOps tooling.

## Getting Started

1. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Set the required environment variables (see `backend/.env.example` if available).
3. Launch the backend API:
   ```bash
   uvicorn app.main:app --reload --app-dir backend
   ```
4. (Optional) Start the frontend development server following the instructions in `frontend/`.

## Testing

Run the backend test suite:
```bash
pytest backend
```

## Contributing

- Follow the existing code style and linting rules.
- Accompany feature work or bug fixes with relevant tests.
- Open a pull request with a clear summary and testing notes.


