from fastapi import APIRouter, Query
from app.api.schemas import (
    HealthResponse,
    OptimizeRequest,
    OptimizeResponse,
)
from app.agents.orchestrator import optimize_routes as optimize_non_llm
from app.agents.orchestrator_llm import optimize_routes_with_llm

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/optimize_routes", response_model=OptimizeResponse)
def optimize(
    request: OptimizeRequest,
    use_llm: bool = Query(default=False, description="Use LLM-based orchestrator"),
) -> OptimizeResponse:
    payload = {
        "vehicles": [v.model_dump() for v in request.vehicles],
        "orders": [o.model_dump() for o in request.orders],
        "constraints": request.constraints or "",
    }

    if use_llm:
        result = optimize_routes_with_llm(payload)
    else:
        result = optimize_non_llm(payload)

    return OptimizeResponse(**result)