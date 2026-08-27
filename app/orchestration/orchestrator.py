from typing import Any, Dict

from app.agents.state import RouteOptimizationState


class RouteOptimizationOrchestrator:
    """
    Application-level orchestrator.

    Commit 1:
        Provides a clean orchestration boundary.

    Future commits:
        This layer will integrate LangGraph and coordinate
        tool selection, validation, and autonomous replanning.
    """

    def run(
        self,
        vehicles: list[Dict[str, Any]],
        delivery_requests: list[Dict[str, Any]],
    ) -> Dict[str, Any]:

        state: RouteOptimizationState = {
            "request_id": "",
            "vehicles": vehicles,
            "delivery_requests": delivery_requests,
            "current_routes": [],
            "candidate_routes": [],
            "vehicle_assignments": [],
            "traffic_conditions": {},
            "eta_predictions": {},
            "optimization_context": {},
            "selected_tool": None,
            "tool_result": None,
            "validation_result": None,
            "decision": None,
            "reasoning": None,
            "replanning_required": False,
            "iteration": 0,
            "final_plan": None,
            "errors": [],
        }

        # Existing deterministic optimization logic will be
        # integrated behind this boundary in the next commits.
        result = self._deterministic_plan(state)

        return result

    def _deterministic_plan(
        self,
        state: RouteOptimizationState,
    ) -> Dict[str, Any]:

        vehicles = state.get("vehicles", [])
        delivery_requests = state.get("delivery_requests", [])

        assignments = []

        for index, request in enumerate(delivery_requests):
            if not vehicles:
                break

            vehicle = vehicles[index % len(vehicles)]

            assignments.append(
                {
                    "request_id": request.get("id", str(index)),
                    "vehicle_id": vehicle.get("id"),
                }
            )

        final_plan = {
            "assignments": assignments,
            "vehicle_count": len(vehicles),
            "delivery_count": len(delivery_requests),
        }

        return {
            "status": "success",
            "plan": final_plan,
            "agent_state": state,
        }