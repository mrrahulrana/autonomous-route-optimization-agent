from app.agents.orchestrator import optimize_routes

def test_optimize_routes_basic():
    payload = {
        "vehicles": [{"id": "v1", "depot_id": 1}],
        "orders": [
            {
                "id": "o1",
                "location_id": 10,
                "distance_km": 10.0,
                "time_of_day": 8,
                "day_of_week": 2,
                "traffic_level": 1,
            }
        ],
        "constraints": "",
    }
    result = optimize_routes(payload)

    assert "routes" in result
    assert "v1" in result["routes"]
    assert result["total_eta_min"] > 0.0