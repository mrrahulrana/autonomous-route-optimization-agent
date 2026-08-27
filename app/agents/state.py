from typing import Any, Dict, List, Optional, TypedDict


class RouteOptimizationState(TypedDict, total=False):
    """
    Shared state passed between agents and tools.

    This state will eventually be used by the LangGraph
    agent workflow for observe -> reason -> act -> validate -> replan.
    """

    request_id: str

    vehicles: List[Dict[str, Any]]
    delivery_requests: List[Dict[str, Any]]

    current_routes: List[Dict[str, Any]]
    candidate_routes: List[Dict[str, Any]]

    vehicle_assignments: List[Dict[str, Any]]

    traffic_conditions: Dict[str, Any]

    eta_predictions: Dict[str, float]

    optimization_context: Dict[str, Any]

    selected_tool: Optional[str]
    tool_result: Optional[Dict[str, Any]]

    validation_result: Optional[Dict[str, Any]]

    decision: Optional[str]
    reasoning: Optional[str]

    replanning_required: bool
    iteration: int

    final_plan: Optional[Dict[str, Any]]

    errors: List[str]