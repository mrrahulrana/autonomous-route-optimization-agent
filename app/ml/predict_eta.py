from pathlib import Path
from typing import List, Dict, Any

import joblib
import pandas as pd
import numpy as np

from app.ml.route_history_store import RouteHistoryStore

ML_DIR = Path(__file__).resolve().parent
MODEL_PATH = ML_DIR / "eta_model.joblib"

_model = None
_history_store = RouteHistoryStore()

FEATURE_COLS = [
    "origin",
    "destination",
    "distance_km",
    "time_of_day",
    "day_of_week",
    "traffic_level",
    "avg_historical_eta_min",
    "num_past_trips",
    "on_time_ratio",
]


def load_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"ETA model not found at {MODEL_PATH}. "
                "Run `python app/ml/train_eta_model.py` first."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def _ensure_history_fields(trip: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure avg_historical_eta_min, num_past_trips, on_time_ratio are present.
    If missing, fill from RouteHistoryStore defaults.
    """
    origin = int(trip["origin"])
    destination = int(trip["destination"])

    # Only fetch history if any of the fields are missing
    if any(
        field not in trip
        for field in ("avg_historical_eta_min", "num_past_trips", "on_time_ratio")
    ):
        history = _history_store.get_route_history(origin, destination)
        trip.setdefault("avg_historical_eta_min", history["avg_historical_eta_min"])
        trip.setdefault("num_past_trips", history["num_past_trips"])
        trip.setdefault("on_time_ratio", history["on_time_ratio"])

    return trip


def predict_eta(trips: List[Dict[str, Any]]) -> np.ndarray:
    """
    Predict ETA (in minutes) for a list of trip segments.

    Each dict should include:
      origin, destination, distance_km, time_of_day, day_of_week, traffic_level.

    Route history fields (avg_historical_eta_min, num_past_trips, on_time_ratio)
    can be provided; if missing, they will be filled using RouteHistoryStore.
    """
    model = load_model()

    enriched_trips = [_ensure_history_fields(dict(trip)) for trip in trips]
    df = pd.DataFrame(enriched_trips)

    # Ensure column order and presence match training
    df = df[FEATURE_COLS]
    
    preds = model.predict(df)
    return preds