# Architecture overview

The Autonomous Route Optimization Agent is structured as a layered, production-style service for fleet route optimization.

## Layers

- **API (`app/api`, `app/main.py`)**
  - FastAPI application exposing `/api/health` and `/api/optimize_routes`.
  - Request/response models defined with Pydantic in `schemas.py`.

- **Agents (`app/agents`)**
  - `allocation_agent`: assigns orders to vehicles.
  - `route_agent`: builds route segments (depot → customer).
  - `traffic_agent`: simulates traffic conditions and adjusts `traffic_level`.
  - `eta_agent`: wraps the XGBoost ETA model and aggregates segment ETAs.
  - `orchestrator`: deterministic, non-LLM orchestration pipeline.
  - `orchestrator_llm`: LangGraph-based orchestration using the agents as tools and an OpenAI LLM to produce explanations. [file:1]

- **ML (`app/ml`)**
  - `train_eta_model.py`: generates synthetic telemetry-style data and trains an XGBoost regression model with time, distance, traffic, and route history features. [file:1]
  - `predict_eta.py`: loads the model and predicts ETAs for route segments, enriching them with route history features from an in-memory store.

- **Services (`app/services`)**
  - `llm_service.py`: configures and provides an OpenAI Chat model client via LangChain (`ChatOpenAI`), based on environment variables. [file:1]

- **Utilities (`app/utils`)**
  - `config.py`: centralised configuration using Pydantic and `python-dotenv`.

This structure mirrors how real-world fleet analytics and ML/GenAI services are built: clear separation of concerns, testable orchestration, and a clean API surface. [file:1]