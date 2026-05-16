# Autonomous Route Optimization Agent

This project demonstrates an agentic AI architecture for fleet route optimization, combining an ETA prediction model, traffic simulation, and LLM-based orchestration, exposed via a FastAPI service. [file:1]

## Status

This first version includes:

- Project structure with clear layering (`api`, `agents`, `ml`, `services`, etc.)
- A minimal FastAPI app with a `/api/health` endpoint
- Environment-based configuration for future ML, LLM, and database components

Subsequent commits will add:

- An XGBoost-based ETA model
- Multi-agent orchestration (planner, ETA, traffic, allocation)
- LangChain/LangGraph-based LLM reasoning
- Dockerization, tests, and documentation