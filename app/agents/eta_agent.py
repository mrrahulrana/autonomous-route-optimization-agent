from typing import List, Dict, Any

from app.ml.predict_eta import predict_eta

def estimate_route_eta(segments: List[Dict[str, Any]]) -> float:
    """
    Given a list of route segments, return total ETA in minutes.
    """
    etas = predict_eta(segments)
    return float(etas.sum())