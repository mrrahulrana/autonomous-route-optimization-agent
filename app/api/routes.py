from fastapi import APIRouter
from app.api.schemas import (
    HealthResponse,
    OptimizeRequest,
    OptimizeResponse,
)
from app.agents.orchestrator import optimize_routes

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/optimize_routes", response_model=OptimizeResponse)
def optimize(request: OptimizeRequest) -> OptimizeResponse:
    payload = {
        "vehicles": [v.model_dump() for v in request.vehicles],
        "orders": [o.model_dump() for o in request.orders],
        "constraints": request.constraints or "",
    }
    result = optimize_routes(payload)
    return OptimizeResponse(**result)