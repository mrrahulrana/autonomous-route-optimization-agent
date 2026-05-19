from typing import List, Dict, Any

def apply_traffic(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Adjust traffic_level based on time_of_day (simple rush hour logic).
    """
    adjusted: List[Dict[str, Any]] = []

    for seg in segments:
        new_seg = dict(seg)
        tod = int(new_seg["time_of_day"])
        base_level = int(new_seg.get("traffic_level", 1))

        # Increase traffic during morning/evening rush hours
        if 7 <= tod <= 9 or 16 <= tod <= 18:
            base_level = min(base_level + 1, 2)

        new_seg["traffic_level"] = base_level
        adjusted.append(new_seg)

    return adjusted