from typing import List, Dict, Any

from app.agents.route_agent import build_segments_from_orders

def allocate_orders_to_vehicles(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Allocation logic placeholder.

    For now, delegates to a simple round-robin route planner.
    """
    vehicles: List[Dict[str, Any]] = payload["vehicles"]
    orders: List[Dict[str, Any]] = payload["orders"]
    return build_segments_from_orders(vehicles, orders)