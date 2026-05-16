from pathlib import Path
from typing import List, Dict, Any

import joblib
import pandas as pd
import numpy as np

ML_DIR = Path(__file__).resolve().parent
MODEL_PATH = ML_DIR / "eta_model.joblib"

_model = None


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


def predict_eta(trips: List[Dict[str, Any]]) -> np.ndarray:
    """
    Predict ETA (in minutes) for a list of trip segments.

    Each dict should include:
      origin, destination, distance_km, time_of_day, day_of_week,
      traffic_level, avg_historical_eta_min, num_past_trips, on_time_ratio
    """
    model = load_model()
    df = pd.DataFrame(trips)
    preds = model.predict(df)
    return preds