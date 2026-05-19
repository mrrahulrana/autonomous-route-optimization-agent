from typing import List, Dict, Any

def build_segments_from_orders(
    vehicles: List[Dict[str, Any]],
    orders: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Simple planner:
    - Assign orders round-robin to vehicles.
    - Each order becomes one segment from depot -> order location.
    """
    segments: List[Dict[str, Any]] = []
    v_count = len(vehicles)

    for idx, order in enumerate(orders):
        vehicle = vehicles[idx % v_count]
        segments.append(
            {
                "vehicle_id": vehicle["id"],
                "order_id": order["id"],
                "origin": vehicle["depot_id"],
                "destination": order["location_id"],
                "distance_km": order["distance_km"],
                "time_of_day": order["time_of_day"],
                "day_of_week": order["day_of_week"],
                # initial traffic_level, may be adjusted by traffic agent
                "traffic_level": order.get("traffic_level", 1),
            }
        )

    return segments