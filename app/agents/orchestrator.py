from typing import Dict, Any, List

from app.agents.allocation_agent import allocate_orders_to_vehicles
from app.agents.traffic_agent import apply_traffic
from app.agents.eta_agent import estimate_route_eta

def optimize_routes(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Non-LLM orchestrator:
    - allocate orders to vehicles
    - apply traffic adjustments
    - estimate total ETA
    - group segments by vehicle
    """
    segments: List[Dict[str, Any]] = allocate_orders_to_vehicles(payload)
    segments_with_traffic = apply_traffic(segments)
    total_eta_min = estimate_route_eta(segments_with_traffic)

    routes: Dict[str, List[Dict[str, Any]]] = {}
    for seg in segments_with_traffic:
        vid = seg["vehicle_id"]
        routes.setdefault(vid, []).append(seg)

    return {
        "routes": routes,
        "total_eta_min": total_eta_min,
        "reasoning": (
            "Round-robin allocation of orders to vehicles with simple traffic "
            "adjustment and ETA aggregation."
        ),
    }