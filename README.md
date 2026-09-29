# CivicPulse - Automated Municipal Complaint Triage System

[![Course: CS4032](https://img.shields.io/badge/Course-CS4032%20Software%20Construction%20%26%20Design-blue.svg)](https://github.com/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.115+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%7C%20TypeScript%20%7C%20Vite-61DAFB.svg?logo=react)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2015+-336791.svg?logo=postgresql)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Cache%20%26%20RateLimit-Redis%207+-DC382D.svg?logo=redis)](https://redis.io)
[![Docker](https://img.shields.io/badge/Deployment-Docker%20Compose-2496ED.svg?logo=docker)](https://www.docker.com)

**CivicPulse** is an enterprise-grade municipal complaint triage platform designed for modern civic authorities. It automatically ingests citizen complaints, triages and categorizes them using pluggable AI/LLM providers (Ollama, Groq, deterministic rule-based engines, and simulated fallback engines), tracks resolution status through a finite state machine, and provides a real-time reactive dashboard for municipal administrators and citizens.

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
  - [Option A: Docker Compose (Recommended)](#option-a-docker-compose-recommended)
  - [Option B: Local / Native Development](#option-b-local--native-development)
- [Step-by-Step Testing & Verification Guide](#step-by-step-testing--verification-guide)
  - [1. Automated Test Suites](#1-automated-test-suites)
  - [2. Operational Health & Metrics Probes](#2-operational-health--metrics-probes)
  - [3. Backend API Contract Verification (cURL / HTTP)](#3-backend-api-contract-verification-curl--http)
  - [4. Frontend UI Interactive Verification](#4-frontend-ui-interactive-verification)
- [Project Directory Structure](#project-directory-structure)
- [Troubleshooting & FAQ](#troubleshooting--faq)
- [Architecture & Governance Documentation](#architecture--governance-documentation)

---

## System Architecture

CivicPulse adheres to a strict **4-layer backend architecture** ensuring clean separation of concerns and deterministic fallback resilience:

```mermaid
graph TD
    Client["Browser / Client (React 18 + Vite)"] -->|HTTP / JSON| Routes["API Routes Layer (FastAPI)"]
    Routes -->|"Check Rate Limit (Sliding Window)"| Redis["Redis 7 (AOF Persistence)"]
    Routes -->|"Invoke Triage / Cache"| Services["Service Orchestration Layer"]
    Services -->|"AI Triage (Ollama / Groq / Rules)"| Providers["Provider Layer"]
    Providers -->|"Failure / Injection Detected"| Fallback["Deterministic Rule-Based Fallback"]
    Services -->|"Cache Hit / Miss (X-Cache)"| Redis
    Services -->|"Persist & Query"| Repositories["Repository Layer (SQLAlchemy 2.0 Async)"]
    Repositories -->|"Transactions & Migrations"| PostgreSQL[("PostgreSQL 15 Database")]
```

For complete architectural details, see [docs/SYSTEM-ARCHITECTURE.md](docs/SYSTEM-ARCHITECTURE.md).

---

## Key Features

1. **Pluggable Multi-Provider AI Triage**:
   - Supports local offline models (**Ollama** with `llama3:8b`), hosted cloud inference (**Groq** with `llama-3.3-70b-versatile`), deterministic **Rule-Based**, and **Simulated** providers.
   - Resilient fallback: Any LLM timeout, malformed JSON response, or prompt injection automatically triggers a zero-downtime fallback to the rule-based engine (`rules:fallback`).
2. **Strict Finite State Machine**:
   - Enforces valid complaint lifecycles: `open` &rarr; `in_progress` &rarr; `resolved` / `rejected`.
   - Invalid or backward transitions return a structured `409 Conflict`.
3. **Distributed Sliding-Window Rate Limiting**:
   - Redis-backed rate limiter on `POST /api/complaints` (default: 10 req/min per IP).
   - Returns standard `429 Too Many Requests` with a dynamic `Retry-After` header.
4. **Read-Through Aggregate Caching**:
   - `GET /api/stats` leverages Redis caching with cache status exposed via the `X-Cache: HIT` or `X-Cache: MISS` HTTP response header.
   - Cache is automatically invalidated upon new complaint creation or status updates.
5. **Modern Glassmorphic UI**:
   - Built with React 18, TypeScript, and Vite.
   - Semantic layouts, accessible forms, 140-character expandable truncation, enum-driven color-coded badges, and live rate-limit countdown alerts.

---

## Prerequisites

Before starting, ensure you have the following installed on your machine:

| Tool | Version Requirement | Purpose |
| :--- | :--- | :--- |
| **Docker & Docker Compose** | Docker v24+ / Compose v2+ | Container orchestration (Recommended) |
| **Python** *(if running locally)* | `>= 3.12` | Backend runtime |
| **Node.js & npm** *(if running locally)* | Node `>= 18.0.0` (LTS recommended) | Frontend runtime and package manager |
| **PostgreSQL** *(if running locally)* | `>= 15.0` | Primary relational database |
| **Redis** *(if running locally)* | `>= 7.0` | Distributed cache and rate limiting |

---

## Environment Configuration

CivicPulse uses a root `.env` file to manage configurations across Docker and local environments.

1. In the project root, create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
   *(On Windows PowerShell: `Copy-Item .env.example .env`)*

2. Review or customize the environment variables:
   ```ini
   # PostgreSQL
   POSTGRES_USER=civic_user
   POSTGRES_PASSWORD=civic_password
   POSTGRES_DB=civicpulse
   DATABASE_URL=postgresql+asyncpg://civic_user:civic_password@localhost:5432/civicpulse

   # Redis
   REDIS_URL=redis://localhost:6379/0

   # Triage Provider Selection: rules | simulated | ollama | groq
   # Default to 'rules' for immediate offline execution without external API keys or Ollama downloads
   TRIAGE_PROVIDER=rules

   # Hosted LLM (Groq) - required only if TRIAGE_PROVIDER=groq
   GROQ_API_KEY=

   # Local LLM (Ollama) - required only if TRIAGE_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434

   # Rate Limiting
   RATE_LIMIT_REQUESTS=10
   RATE_LIMIT_WINDOW_SECONDS=60

   # CORS Allowed Origins
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

---

## Running the Application

### Option A: Docker Compose (Recommended)

Docker Compose starts the entire ecosystem: PostgreSQL, Redis (with Append-Only File persistence), Ollama, Backend (FastAPI), and Frontend (Nginx multi-stage build).

#### 1. Build and Launch Containers
```bash
docker compose up --build -d
```

Verify that all 5 containers are healthy and running:
```bash
docker compose ps
```

#### 2. Apply Database Migrations
Run the Alembic migration command inside the backend container to create all tables and indexes:
```bash
docker compose exec backend alembic upgrade head
```

#### 3. Seed Realistic Complaint Data
Seed the database with 30+ realistic municipal complaints (idempotent, safe to run multiple times):
```bash
docker compose exec backend python -m scripts.seed
```

#### 4. Access the Application
- **Frontend Dashboard & Form**: [http://localhost:3000](http://localhost:3000)
- **Backend API Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend OpenAPI Specification**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **Prometheus Metrics**: [http://localhost:8000/metrics](http://localhost:8000/metrics)

#### 5. Stop the Containers
```bash
# Stop containers while preserving volume data
docker compose down

# Or stop and clear all container volumes
docker compose down -v
```

---

### Option B: Local / Native Development

If you prefer to run services natively without Docker containers:

#### 1. Start Database & Redis
Ensure PostgreSQL is running on port `5432` with a database named `civicpulse`, and Redis is running on port `6379`.

#### 2. Backend Setup
Navigate to the `backend/` directory:
```bash
cd backend
```

Create and activate a Python 3.12 virtual environment:
- **macOS / Linux**:
  ```bash
  python3.12 -m venv .venv
  source .venv/bin/activate
  ```
- **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

Install backend dependencies in editable mode:
```bash
pip install -e ".[dev]"
```

Run database migrations:
```bash
alembic upgrade head
```

Seed initial complaint data:
```bash
python scripts/seed.py
```

Start the FastAPI development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*The backend is now live at [http://localhost:8000](http://localhost:8000).*

#### 3. Frontend Setup
Open a new terminal window and navigate to the `frontend/` directory:
```bash
cd frontend
```

Install frontend npm packages:
```bash
npm install
```

Start the Vite development server:
```bash
npm run dev
```
*The frontend development server is now running (typically at [http://localhost:5173](http://localhost:5173) or [http://localhost:3000](http://localhost:3000)).*

---

## Step-by-Step Testing & Verification Guide

Follow these sequential steps to thoroughly test and verify all functional, architectural, and security contracts of CivicPulse.

### 1. Automated Test Suites

#### Backend Test Suite (Pytest)
Run the complete backend test suite:
```bash
# From the backend directory with virtual environment activated:
pytest -v --tb=short
```

To run with test coverage reporting:
```bash
pytest --cov=app --cov-report=term-missing
```
*Expected result:* 100% of tests pass, validating health probes, request ID propagation, Pydantic input validation, status state machine transitions, and AI triage fallback mechanisms.

#### Backend Static Analysis & Type Checking
```bash
# Linting check
ruff check .

# Static type verification
mypy app
```

#### Frontend Test Suite (Vitest)
Navigate to the `frontend/` directory:
```bash
cd frontend
npm test
```
*Expected result:* Vitest executes unit tests validating domain types, enum consistency, and component mounting.

#### Frontend Linting & Type Checking
```bash
npm run type-check
npm run lint
```

---

### 2. Operational Health & Metrics Probes

Verify operational probes required for production readiness and container orchestration:

#### Liveness Probe (`GET /health`)
The liveness probe guarantees that the process is alive without touching external databases or caches:
```bash
curl -i http://localhost:8000/health
```
*Expected Output:*
```http
HTTP/1.1 200 OK
content-type: application/json
X-Request-ID: <auto-generated-uuid>

{"status":"alive"}
```

#### Request ID Propagation (`X-Request-ID`)
Verify that a client-provided `X-Request-ID` is preserved throughout the request lifecycle:
```bash
curl -i -H "X-Request-ID: test-trace-uuid-101" http://localhost:8000/health
```
*Expected Output:*
Verify that `X-Request-ID: test-trace-uuid-101` is echoed in the response headers.

#### Readiness Probe (`GET /ready`)
The readiness probe validates live connectivity to PostgreSQL and Redis:
```bash
curl -i http://localhost:8000/ready
```
*Expected Output:*
```http
HTTP/1.1 200 OK
content-type: application/json

{"status":"ready"}
```

#### Prometheus Metrics (`GET /metrics`)
Exposes operational metrics in standard Prometheus exposition format:
```bash
curl -s http://localhost:8000/metrics | grep http_requests_total
```

---

### 3. Backend API Contract Verification (cURL / HTTP)

#### Test 3.1: Submit Complaint with Automated AI Triage
Submit a realistic complaint requiring classification:
```bash
curl -X POST http://localhost:8000/api/complaints \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Huge water leakage from broken underground pipe flooding Main Boulevard",
    "location": "Main Boulevard, Gulberg III",
    "reporter_contact": "citizen@example.com"
  }'
```
*Expected Output (Status 201 Created):*
```json
{
  "id": "e6a12b45-...",
  "text": "Huge water leakage from broken underground pipe flooding Main Boulevard",
  "location": "Main Boulevard, Gulberg III",
  "category": "water",
  "priority": "high",
  "status": "open",
  "ai_summary": "Water pipe leak causing street flooding",
  "triaged_by": "rules",
  "created_at": "..."
}
```

#### Test 3.2: 400 Bad Request Input Validation Contract
Verify that invalid payloads (such as complaints with text under 10 characters) return standard `400 Bad Request` instead of FastAPI's default 422:
```bash
curl -i -X POST http://localhost:8000/api/complaints \
  -H "Content-Type: application/json" \
  -d '{"text": "Short", "location": "Lahore"}'
```
*Expected Output:*
```http
HTTP/1.1 400 Bad Request
content-type: application/json

{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "text"],
      "msg": "String should have at least 10 characters"
    }
  ]
}
```

#### Test 3.3: 429 Too Many Requests Rate Limiting
Execute 11 rapid requests within 60 seconds from the same client IP:
```bash
# On Linux/macOS bash:
for i in {1..12}; do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/api/complaints \
    -H "Content-Type: application/json" \
    -d '{"text": "Water leakage test for rate limiting enforcement", "location": "Test Area"}'
done
```
*(On Windows PowerShell: `1..12 | ForEach-Object { (Invoke-WebRequest -Method Post -Uri "http://localhost:8000/api/complaints" -ContentType "application/json" -Body '{"text":"Water leakage test for rate limiting","location":"Test"}').StatusCode }`)*

*Expected Output:*
The 11th and 12th requests return HTTP `429 Too Many Requests` with a `Retry-After: <seconds>` header.

#### Test 3.4: Status State Machine & 409 Conflict Contract
Retrieve the ID of a newly created complaint, then attempt valid and invalid status transitions.

1. **Valid Transition (`open` &rarr; `in_progress`):**
   ```bash
   curl -i -X PATCH http://localhost:8000/api/complaints/<COMPLAINT_ID>/status \
     -H "Content-Type: application/json" \
     -d '{"status": "in_progress"}'
   ```
   *Expected Output:* `HTTP/1.1 200 OK` with `"status": "in_progress"`.

2. **Invalid Transition (`in_progress` &rarr; `open`):**
   ```bash
   curl -i -X PATCH http://localhost:8000/api/complaints/<COMPLAINT_ID>/status \
     -H "Content-Type: application/json" \
     -d '{"status": "open"}'
   ```
   *Expected Output:*
   ```http
   HTTP/1.1 409 Conflict
   content-type: application/json

   {"detail": "Invalid transition from in_progress to open"}
   ```

3. **Terminal State Immutability (`resolved` &rarr; any):**
   First transition to `resolved`:
   ```bash
   curl -X PATCH http://localhost:8000/api/complaints/<COMPLAINT_ID>/status \
     -H "Content-Type: application/json" \
     -d '{"status": "resolved"}'
   ```
   Now attempt to move back to `in_progress`:
   ```bash
   curl -i -X PATCH http://localhost:8000/api/complaints/<COMPLAINT_ID>/status \
     -H "Content-Type: application/json" \
     -d '{"status": "in_progress"}'
   ```
   *Expected Output:* `HTTP/1.1 409 Conflict`.

#### Test 3.5: Read-Through Cache & `X-Cache` Header Verification
Query the aggregate statistics endpoint:
```bash
# First request: Cache Miss
curl -i http://localhost:8000/api/stats
```
*Expected Header:* `X-Cache: MISS`

Query again immediately:
```bash
# Second request: Cache Hit
curl -i http://localhost:8000/api/stats
```
*Expected Header:* `X-Cache: HIT`

Submit a new complaint or update a status:
```bash
# Triggers cache invalidation in Redis
curl -X POST http://localhost:8000/api/complaints \
  -H "Content-Type: application/json" \
  -d '{"text": "Pothole in the road near Sector G-10", "location": "Islamabad"}'
```
Query stats again:
```bash
curl -i http://localhost:8000/api/stats
```
*Expected Header:* `X-Cache: MISS` (invalidated and re-cached).

---

### 4. Frontend UI Interactive Verification

Open your browser and navigate to **[http://localhost:3000](http://localhost:3000)** (or `http://localhost:5173` if running Vite locally).

#### Verification Flow 1: Submit Complaint Page (`/`)
1. Click **Submit Complaint** in the navigation bar.
2. Enter a description with less than 10 characters (e.g., "Leak") and click **Submit Complaint**.
   - *Verify:* The form displays a client-side warning, and backend 400 responses appear in the stylized `ApiErrorBanner` without crashing the application.
3. Enter valid complaint details:
   - **Description**: *"Severe sewage line overflow outside building 4A causing foul odor and health hazard"*
   - **Location**: *"Block 5, Clifton, Karachi"*
   - **Contact**: *"resident@example.com"*
4. Click **Submit Complaint**.
   - *Verify:* The button shows a loading spinner, and upon success, you are redirected to the **Dashboard** with the newly triaged complaint at the top.

#### Verification Flow 2: Complaints Dashboard (`/dashboard`)
1. Navigate to the **Dashboard**.
2. **140-Character Truncation**:
   - Long complaints show truncated text with a clickable `Read more` button.
   - Click `Read more` to expand the full description, and `Read less` to collapse.
3. **Filtering & Pagination**:
   - Filter by Category (e.g., `water`, `electricity`, `roads`, `sanitation`).
   - Filter by Priority (`high`, `normal`, `low`) or Status (`open`, `in_progress`, `resolved`).
   - Use pagination controls to move between pages.
4. **State Machine Action Controls**:
   - For an `open` complaint, verify that only the **Start Progress** and **Reject** buttons are active.
   - Click **Start Progress** &rarr; status updates to `in_progress` with an updated badge color.
   - For an `in_progress` complaint, verify that **Resolve** and **Reject** buttons are active, while backward transitions are disabled.

#### Verification Flow 3: Real-Time Statistics & Cache Indicator (`/stats`)
1. Navigate to **Statistics**.
2. Inspect the aggregate cards:
   - Total complaints count.
   - Breakdown charts by Category, Priority, and Status.
3. Observe the **Cache Performance** indicator badge:
   - Displays `Cache Status: HIT` or `Cache Status: MISS` corresponding to the `X-Cache` HTTP header.
   - Refreshing the page displays `HIT` with minimal latency.

#### Verification Flow 4: Rate Limit Banner Alert
1. In rapid succession, submit 11 complaints on the submission page.
2. Observe the persistent floating `429 Too Many Requests` alert banner:
   - Displays: *"Rate limit exceeded. Please wait X seconds before retrying."*
   - Shows a live countdown timer decrementing each second until requests are re-enabled.

---

## Project Directory Structure

```text
CivicPulse/
├── .env.example                     # Environment template
├── docker-compose.yml               # Multi-container orchestration specification
├── docs/                            # Formal system documentation
│   ├── SYSTEM-ARCHITECTURE.md       # 4-layer architecture, caching, & concurrency
│   ├── DATA-GOVERNANCE.md           # PII redaction policy & retention rules
│   └── IMPLEMENTATION-STATUS.md     # Audit report & phase execution tracking
├── backend/
│   ├── Dockerfile                   # Python 3.12 slim container definition
│   ├── pyproject.toml               # Poetry/pip build configuration & dependencies
│   ├── alembic.ini                  # Migration configuration
│   ├── alembic/                     # Database migration revisions
│   │   └── versions/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & middleware
│   │   ├── config.py                # Pydantic Settings configuration
│   │   ├── database.py              # Async SQLAlchemy engine & session factory
│   │   ├── models.py                # Domain models, Enums, & State Machine logic
│   │   ├── routes/                  # Layer 1: HTTP API Routers
│   │   │   ├── complaints.py        # Complaint ingestion, listing, & status updates
│   │   │   ├── health.py            # Liveness, readiness, & Prometheus metrics
│   │   │   └── meta.py              # Stats & provider metadata routes
│   │   ├── services/                # Layer 2: Business & Orchestration Services
│   │   │   ├── rate_limiter.py      # Redis sliding-window distributed rate limiter
│   │   │   ├── stats.py             # Read-through statistics aggregator
│   │   │   ├── stats_cache.py       # Stats cache invalidation service
│   │   │   └── triage_cache.py      # AI triage response caching
│   │   ├── repositories/            # Layer 3: Database Access & Persistence
│   │   │   ├── complaint.py         # SQLAlchemy complaint repository & filters
│   │   │   └── models.py            # PostgreSQL table schema definitions
│   │   └── providers/               # Layer 4: External Integrations & AI Models
│   │       ├── redis.py             # Redis connection provider
│   │       └── triage/              # Pluggable triage provider implementations
│   │           ├── protocol.py      # TriageProvider typing protocol
│   │           ├── factory.py       # TriageOrchestrator & provider factory
│   │           ├── rule_based.py    # Deterministic regex/keyword classifier
│   │           ├── simulated.py     # Testing provider with failure injection
│   │           ├── ollama.py        # Local Ollama LLM provider
│   │           └── llm.py           # Hosted Groq cloud LLM provider
│   ├── scripts/
│   │   └── seed.py                  # Idempotent database seeder (30+ complaints)
│   └── tests/                       # Backend test suite (Pytest)
│       ├── test_foundation.py       # Smoke, enum, & state machine tests
│       ├── test_routes.py           # HTTP contract & 400 validation tests
│       └── test_triage.py           # Provider failure & injection fallback tests
└── frontend/
    ├── Dockerfile                   # Multi-stage Node build -> Nginx distribution
    ├── nginx.conf                   # Production Nginx reverse-proxy & routing config
    ├── package.json                 # Frontend dependencies & scripts
    ├── tsconfig.json                # TypeScript compiler configuration
    ├── vite.config.ts               # Vite bundler configuration
    ├── src/
    │   ├── main.tsx                 # React DOM mount point
    │   ├── App.tsx                  # Top-level routing & layout shell
    │   ├── App.css                  # Modern glassmorphic theme & color tokens
    │   ├── api/
    │   │   ├── client.ts            # Typed HTTP client & error handler
    │   │   └── types.ts             # Domain interfaces matching backend contracts
    │   ├── components/
    │   │   ├── ApiErrorBanner.tsx   # 400/429 error presentation & retry countdown
    │   │   ├── ErrorBoundary.tsx    # React crash boundary
    │   │   └── StatusBadge.tsx      # Color-coded state badge component
    │   └── pages/
    │       ├── DashboardPage.tsx    # Paginated complaints grid & status actions
    │       ├── SubmitPage.tsx       # Citizen complaint submission form
    │       └── StatsPage.tsx        # Analytics charts & X-Cache monitor
    └── tests/                       # Frontend unit & component tests (Vitest)
```

---

## Troubleshooting & FAQ

### 1. Port Conflicts (e.g., Port 8000 or 5432 already in use)
- **Symptom**: `Bind for 0.0.0.0:8000 failed: port is already allocated`.
- **Solution**: Check if another PostgreSQL or local server is running:
  - Windows: `netstat -ano | findstr :8000`
  - Linux/Mac: `lsof -i :8000`
  - Either terminate the conflicting process or change the exposed port in `docker-compose.yml`.

### 2. Database Connection Errors on Startup
- **Symptom**: Backend logs show `asyncpg.exceptions.CannotConnectNowError`.
- **Solution**: The `docker-compose.yml` includes strict healthchecks (`pg_isready`). When running natively, ensure the PostgreSQL service is fully initialized and credentials in `.env` match your local PostgreSQL configuration.

### 3. Using Local Ollama AI Triage
- If `TRIAGE_PROVIDER=ollama`:
  1. Ensure Ollama is running (`ollama serve`).
  2. Pull the model before submitting complaints:
     ```bash
     docker compose exec ollama ollama pull llama3:8b
     # Or natively:
     ollama pull llama3:8b
     ```
  3. If Ollama is offline or unavailable, the system automatically falls back to `rules:fallback` without crashing.

### 4. Resetting the Database Completely
To wipe all data and start completely fresh:
```bash
docker compose down -v
docker compose up -d
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed.py
```

---

## Architecture & Governance Documentation

For comprehensive engineering standards, see the documentation in `docs/`:
- **[System Architecture (SYSTEM-ARCHITECTURE.md)](docs/SYSTEM-ARCHITECTURE.md)**: Deep dive into the 4-layer design, state transition tables, caching invalidation strategies, and concurrency control.
- **[Data Governance (DATA-GOVERNANCE.md)](docs/DATA-GOVERNANCE.md)**: Citizen PII anonymization policies, data retention schedules, and prompt injection defense strategies.
- **[Implementation Status (IMPLEMENTATION-STATUS.md)](docs/IMPLEMENTATION-STATUS.md)**: Phase-by-phase completion report and audit verification.
