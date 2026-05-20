from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_optimize_routes_non_llm():
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
    resp = client.post("/api/optimize_routes", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "routes" in data
    assert "v1" in data["routes"]
    assert data["total_eta_min"] > 0