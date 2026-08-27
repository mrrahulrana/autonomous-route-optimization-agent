from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="Autonomous Fleet Route Optimization Agent",
    description=(
        "Agentic AI platform for fleet route optimization "
        "using predictive ML, LLM reasoning and operational tools."
    ),
    version="0.2.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "service": "autonomous-route-optimization-agent",
        "status": "running",
        "version": "0.2.0",
    }