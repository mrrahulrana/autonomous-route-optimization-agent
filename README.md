# Autonomous Route Optimization Agent

An agentic AI service for fleet route optimization. It combines a multi-agent pipeline (allocation, routing, traffic, ETA prediction), an XGBoost-based ETA model, and an optional LangGraph + OpenAI orchestration layer that produces a natural-language explanation of the generated route plan — all exposed via a FastAPI service.

---

## Table of contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Repository structure](#repository-structure)
- [Tech stack](#tech-stack)
- [API reference](#api-reference)
- [Getting started](#getting-started)
- [Running with Docker](#running-with-docker)
- [ETA model](#eta-model)
- [Testing](#testing)
- [Future enhancements](#future-enhancements)

---

## Overview

The service accepts a set of vehicles and orders and returns an optimized set of routes, an aggregated ETA, and a human-readable explanation of the plan. It supports two orchestration modes:

- **Deterministic pipeline** — fast, rule-based allocation + traffic adjustment + ML-based ETA, with a templated explanation.
- **LLM-assisted pipeline** (`use_llm=true`) — runs the same agents as LangGraph tool nodes, then asks an OpenAI model to summarize the plan in plain language, with a graceful fallback to the deterministic explanation if the LLM call fails.

---

## Architecture

### Component diagram

```mermaid
flowchart TB
    Client["Client"] -->|"POST /api/optimize_routes"| API["FastAPI app (app/main.py, app/api/routes.py)"]

    API --> Orchestrator["Orchestrator (app/agents/orchestrator.py)"]
    API --> OrchestratorLLM["LLM Orchestrator - LangGraph (app/agents/orchestrator_llm.py)"]

    subgraph Agents ["Agent layer (app/agents)"]
        Alloc["Allocation Agent"]
        Route["Route Agent"]
        Traffic["Traffic Agent"]
        ETA["ETA Agent"]
    end

    Orchestrator --> Alloc --> Route
    Orchestrator --> Traffic
    Orchestrator --> ETA

    OrchestratorLLM --> Alloc
    OrchestratorLLM --> Traffic
    OrchestratorLLM --> ETA
    OrchestratorLLM --> LLM["LLM Service - ChatOpenAI (app/services/llm_service.py)"]
    LLM --> Prompt["Prompt template (app/prompts/optimization_prompt.txt)"]

    ETA --> Model["XGBoost ETA model (app/ml/predict_eta.py, eta_model.joblib)"]
    Model --> History["Route History Store (app/ml/route_history_store.py)"]

    Config["Settings - .env (app/utils/config.py)"] -.-> API
    Config -.-> LLM
    Config -.-> DB[("PostgreSQL")]
```

### Request flow (sequence)

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI Routes
    participant O as Orchestrator
    participant A as Allocation Agent
    participant R as Route Agent
    participant T as Traffic Agent
    participant E as ETA Agent (XGBoost)
    participant L as LLM Service (optional)

    C->>API: POST /api/optimize_routes?use_llm=...
    API->>O: optimize_routes(vehicles, orders, constraints)
    O->>A: allocate orders to vehicles
    A->>R: build_segments_from_orders()
    O->>T: adjust traffic_level per segment (rush hour aware)
    O->>E: predict_eta(segments)
    E->>E: enrich with route history features
    E-->>O: per-segment ETA + total ETA

    alt use_llm = true
        O->>L: summarize plan (segments, total ETA, constraints)
        L-->>O: natural-language reasoning (or fallback on error)
    else use_llm = false
        O->>O: deterministic reasoning string
    end

    O-->>API: routes, total_eta_min, reasoning
    API-->>C: OptimizeResponse (JSON)
```

### ETA model lifecycle

```mermaid
flowchart LR
    Gen["generate_synthetic_telemetry()"] --> CSV["data/synthetic_trips.csv"]
    CSV --> Train["train_eta_model.py - XGBoost regressor"]
    Train --> Artifact["app/ml/eta_model.joblib"]
    Artifact --> Predict["predict_eta.py"]
    History[("Route History Store - in-memory")] --> Predict
    Predict --> ETAAgent["ETA Agent"]
```

---

## Repository structure

```text
.
├── app/
│   ├── main.py                  # FastAPI application entry point
│   ├── api/
│   │   ├── routes.py            # /api/health, /api/optimize_routes
│   │   └── schemas.py           # Pydantic request/response models
│   ├── agents/
│   │   ├── allocation_agent.py  # Assigns orders to vehicles
│   │   ├── route_agent.py       # Builds route segments from orders
│   │   ├── traffic_agent.py     # Simulates/adjusts traffic_level
│   │   ├── eta_agent.py         # Wraps ETA model, aggregates ETAs
│   │   ├── orchestrator.py       # Deterministic, non-LLM pipeline
│   │   └── orchestrator_llm.py  # LangGraph-based LLM orchestration
│   ├── ml/
│   │   ├── train_eta_model.py   # Synthetic data + XGBoost training
│   │   ├── predict_eta.py       # ETA inference
│   │   ├── predict_eta_test.py  # Ad-hoc prediction script
│   │   └── route_history_store.py # In-memory route history
│   ├── services/
│   │   └── llm_service.py       # ChatOpenAI client (LangChain)
│   ├── prompts/
│   │   └── optimization_prompt.txt # LLM system prompt
│   └── utils/
│       └── config.py            # Pydantic Settings (.env)
├── data/                         # Synthetic telemetry datasets
├── docker/
│   └── Dockerfile               # Builds image, trains ETA model, runs API
├── docs/
│   ├── architecture.md          # Architecture notes
│   └── diagrams/                # Diagram assets
├── notebooks/
│   └── eta_model_experiments.ipynb
├── tests/
│   ├── test_api.py
│   ├── test_route_optimization.py
│   └── test_eta_model.py
├── docker-compose.yml           # API + PostgreSQL
└── requirements.txt
```

---

## Tech stack

| Layer            | Technology |
|------------------|------------|
| API framework    | FastAPI, Uvicorn |
| Agent orchestration | LangGraph, LangChain |
| LLM              | OpenAI (`gpt-4o-mini` by default, via `langchain-openai`) |
| ML model         | XGBoost (ETA regression), scikit-learn |
| Data handling    | pandas, numpy, joblib |
| Validation/config| Pydantic, Pydantic Settings, python-dotenv |
| Database         | PostgreSQL 16 (via SQLAlchemy / psycopg2) |
| Testing          | pytest |
| Containerization | Docker, docker-compose |
| Notebooks        | Jupyter (`notebooks/eta_model_experiments.ipynb`) |

---

## API reference

### `GET /api/health`

Health check.

**Response**
```json
{ "status": "ok" }
```

### `POST /api/optimize_routes`

Optimizes vehicle routes for a given set of orders.

**Query parameters**

| Name      | Type    | Default | Description |
|-----------|---------|---------|-------------|
| `use_llm` | boolean | `false` | If `true`, runs the LangGraph + OpenAI orchestration and adds an LLM-generated explanation. |

**Request body**

```json
{
  "vehicles": [
    { "id": "V1", "depot_id": 1 }
  ],
  "orders": [
    {
      "id": "O1",
      "location_id": 12,
      "distance_km": 8.5,
      "time_of_day": 17,
      "day_of_week": 2,
      "traffic_level": 1
    }
  ],
  "constraints": "Prioritize shorter routes during rush hour"
}
```

**Response**

```json
{
  "routes": {
    "V1": [
      {
        "vehicle_id": "V1",
        "order_id": "O1",
        "origin": 1,
        "destination": 12,
        "distance_km": 8.5,
        "time_of_day": 17,
        "day_of_week": 2,
        "traffic_level": 2,
        "eta_min": 23.4
      }
    ]
  },
  "total_eta_min": 23.4,
  "reasoning": "Plan assigns 1 order across 1 vehicle. Traffic adjusted for rush hour. ..."
}
```

---

## Getting started

### Prerequisites

- Python 3.11+
- (Optional) PostgreSQL 16, if you want to use the `DATABASE_URL` configuration
- An OpenAI API key (only required for `use_llm=true`)

### Local setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
# Create a .env file based on the variables below
#   OPENAI_API_KEY=sk-...
#   MODEL_NAME=gpt-4o-mini
#   DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/route_agent

# 4. Train the ETA model (creates app/ml/eta_model.joblib)
python app/ml/train_eta_model.py

# 5. Run the API
uvicorn app.main:app --reload
```

The API is then available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

### Example request

```bash
curl -X POST "http://127.0.0.1:8000/api/optimize_routes?use_llm=true" \
  -H "Content-Type: application/json" \
  -d '{
        "vehicles": [{"id": "V1", "depot_id": 1}],
        "orders": [
          {"id": "O1", "location_id": 12, "distance_km": 8.5, "time_of_day": 17, "day_of_week": 2}
        ],
        "constraints": "Prioritize shorter routes during rush hour"
      }'
```

---

## Running with Docker

```bash
docker-compose up --build
```

This will:

- Build the API image (`docker/Dockerfile`), which installs dependencies and trains the ETA model at build time
- Start the FastAPI service on `http://localhost:8000`
- Start a PostgreSQL 16 instance on port `5432` (database `route_agent`)

---

## ETA model

The ETA prediction component is an XGBoost regression model trained on synthetic telemetry-style trip data.

```bash
python app/ml/train_eta_model.py
```

This script:

- Generates `data/synthetic_trips.csv` (5,000 synthetic trips)
- Trains an XGBoost regressor using features: origin, destination, distance, time-of-day, day-of-week, traffic level, and route-history features (average historical ETA, number of past trips, on-time ratio)
- Saves the trained model to `app/ml/eta_model.joblib`

At inference time, `app/ml/predict_eta.py` loads the cached model and enriches incoming segments with route-history features from the in-memory `RouteHistoryStore` (`app/ml/route_history_store.py`) when they aren't provided.

---

## Testing

```bash
pytest
```

Covers:

- `tests/test_api.py` — `/api/health` and `/api/optimize_routes` (non-LLM path)
- `tests/test_route_optimization.py` — orchestrator pipeline directly
- `tests/test_eta_model.py` — ETA model predictions

---

## Future enhancements

- **Persistence**: replace the in-memory `RouteHistoryStore` with PostgreSQL-backed storage (the `DATABASE_URL` and SQLAlchemy dependency are already in place but unused)
- **Real-world data integration**: replace synthetic telemetry with live GPS/traffic feeds (e.g. Google Maps, HERE, or OSRM)
- **Smarter allocation**: move from round-robin allocation to capacity- and constraint-aware vehicle assignment (e.g. VRP solver, OR-Tools)
- **Dynamic traffic simulation**: integrate real-time traffic data instead of static rush-hour heuristics
- **Multi-step LLM planning**: extend `orchestrator_llm.py` to allow the LLM to propose route adjustments, not just summarize them
- **Authentication & rate limiting** on the API layer
- **Observability**: structured logging, tracing, and metrics for agent and LLM calls
- **Model retraining pipeline**: scheduled retraining of the ETA model on fresh trip data, with versioned artifacts
- **Frontend dashboard**: a simple UI for visualizing routes, ETAs, and LLM reasoning on a map
- **CI/CD**: automated test and build pipeline (e.g. GitHub Actions) building on the existing `pytest` suite and Dockerfile
