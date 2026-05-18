from typing import Tuple, Dict, Any

class RouteHistoryStore:
    """
    In-memory store for route history features.

    In a real system this would be backed by a database or feature store.
    Here we use a simple dict keyed by (origin, destination).
    """

    def __init__(self) -> None:
        self._store: Dict[Tuple[int, int], Dict[str, Any]] = {}

    def set_route_history(
        self,
        origin: int,
        destination: int,
        avg_historical_eta_min: float,
        num_past_trips: int,
        on_time_ratio: float,
    ) -> None:
        self._store[(origin, destination)] = {
            "avg_historical_eta_min": avg_historical_eta_min,
            "num_past_trips": num_past_trips,
            "on_time_ratio": on_time_ratio,
        }

    def get_route_history(self, origin: int, destination: int) -> Dict[str, Any]:
        """
        Returns route history features for (origin, destination).

        If no history exists, returns reasonable default values.
        """
        key = (origin, destination)
        if key in self._store:
            return self._store[key]

        # Defaults for unseen routes:
        # avg_historical_eta_min: simple heuristic based on notional distance,
        # num_past_trips: 0, on_time_ratio: conservative 0.8
        # (Distance-based logic can be refined later by agents.)
        return {
            "avg_historical_eta_min": 30.0,
            "num_past_trips": 0,
            "on_time_ratio": 0.8,
        }