# ADR 001 — Technology Stack and Architecture for AI-Powered Requirement Analyzer

**Status:** Accepted

## Context

The AI-Powered Requirement Analyzer aims to transform informal user input into structured Product Requirements Documents (PRDs). The project requires a lightweight backend capable of:

- Accepting plain-text input from users
- Processing that input with an AI model (initially a stub, later OpenAI/Anthropic)
- Storing projects, user inputs, and generated PRDs persistently
- Returning structured data via a simple REST API

Key constraints include:
- **Simplicity:** The initial version must be small and easy to deploy by a single developer
- **Limited resources:** No distributed systems, external databases, or message queues at this stage
- **Rapid iteration:** The goal is to get a functional prototype working quickly before optimizing for scale
- **Extensibility:** The architecture should be simple to extend later if features like job queues or integrations are needed

The solution must balance speed of development, maintainability, and a clear growth path toward more advanced features.

## Decision

We will implement the backend as a single-file FastAPI application in Python, using the following technologies:

- **FastAPI** for building the REST API
  - Chosen for its speed, async support, and automatic OpenAPI documentation
- **SQLModel (with SQLite)** for data storage
  - Provides a unified ORM and Pydantic-style data validation while keeping setup minimal
  - SQLite ensures zero-configuration persistence suitable for local development and MVP deployment
- **BackgroundTasks (FastAPI built-in)** for running the AI analysis asynchronously
  - Avoids the need for Celery, Redis, or other job queues at MVP stage
- **HTTPX** for potential asynchronous API calls to AI providers
- **Uvicorn** as the ASGI server for running the FastAPI app

The system will be packaged as a single Python file (`main.py`) for maximum simplicity.
All core logic (data models, API routes, AI stub) will reside within this file until the project matures.

**Alternatives considered:**
- **Flask:** simpler but lacks built-in async and automatic docs generation
- **Django:** powerful but overkill for a lightweight prototype
- **PostgreSQL/MySQL:** better for scaling but unnecessary complexity for early-stage development
- **Celery/Redis:** robust background job handling, deferred for future versions

## Consequences

**Positive Outcomes:**
- Extremely fast development cycle (one-file backend)
- Minimal dependencies and setup — easy for any developer to clone and run
- Clear upgrade path to more complex architectures later (e.g., replacing SQLite with PostgreSQL)
- Built-in interactive API docs via FastAPI's Swagger UI

**Negative Outcomes / Trade-offs:**
- **Scalability limits:** SQLite and FastAPI's in-process background tasks are not suitable for high-concurrency workloads
- **Single-threaded jobs:** Long-running AI calls could block if not carefully handled
- **Maintainability risk:** Keeping all logic in one file can become messy if the codebase grows
- **No persistent job queue:** Failed background tasks aren't retried automatically

**Technical Debt and Risks:**
- Future migration to a real database (e.g., PostgreSQL) will require schema migration and ORM adjustments
- Moving to distributed background processing (e.g., Celery + Redis) will require refactoring job logic
- Adding authentication or multi-user support will require structural changes
Overall, this decision prioritizes developer velocity, simplicity, and functional clarity over scalability and robustness — a deliberate trade-off for an early-stage prototype.
