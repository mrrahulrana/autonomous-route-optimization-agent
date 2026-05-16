from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
import joblib

ROOT_DIR = Path(__file__).resolve().parents[2]  # repo root
DATA_DIR = ROOT_DIR / "data"
ML_DIR = ROOT_DIR / "app" / "ml"

DATA_DIR.mkdir(exist_ok=True, parents=True)
ML_DIR.mkdir(exist_ok=True, parents=True)


def generate_synthetic_telemetry(n_rows: int = 5000) -> pd.DataFrame:
    """
    Generate synthetic 'trip' data with features similar to fleet telemetry:
    origin, destination, distance, time of day, day of week, traffic level,
    plus simple route history features.
    """
    rng = np.random.default_rng(42)

    origins = rng.integers(1, 50, size=n_rows)
    destinations = rng.integers(1, 50, size=n_rows)
    distance_km = rng.uniform(1, 50, size=n_rows)
    time_of_day = rng.integers(0, 24, size=n_rows)
    day_of_week = rng.integers(0, 7, size=n_rows)
    traffic_level = rng.integers(0, 3, size=n_rows)  # 0=low, 1=medium, 2=high

    base_speed = 40.0  # km/h
    traffic_factor = 1.0 + 0.3 * traffic_level

    rush_hour_mask = ((time_of_day >= 7) & (time_of_day <= 9)) | (
        (time_of_day >= 16) & (time_of_day <= 18)
    )
    rush_hour_penalty = np.where(rush_hour_mask, 1.3, 1.0)

    # Base ETA in minutes from physics-ish model
    base_eta_min = (distance_km / base_speed) * 60.0 * traffic_factor * rush_hour_penalty

    # --- Route history features (synthetic) ---
    # Use origin+destination to derive a stable "route id"
    route_id = origins * 1000 + destinations

    # For each route, derive a consistent avg_eta and reliability
    # (we use route_id to seed randomness so it's stable per route)
    route_noise = (route_id % 10) / 10.0  # 0.0 .. 0.9
    avg_historical_eta_min = base_eta_min * (0.9 + 0.2 * route_noise)

    num_past_trips = rng.integers(5, 200, size=n_rows)
    on_time_ratio = 0.7 + 0.3 * route_noise  # 0.7 .. 1.0

    # Final observed ETA with some noise and on-time influence
    eta_noise = rng.normal(0, 3, size=n_rows)
    eta_min = base_eta_min * (1.0 + (1 - on_time_ratio) * 0.2) + eta_noise
    eta_min = np.clip(eta_min, 5, None)

    df = pd.DataFrame(
        {
            "origin": origins,
            "destination": destinations,
            "distance_km": distance_km,
            "time_of_day": time_of_day,
            "day_of_week": day_of_week,
            "traffic_level": traffic_level,
            "avg_historical_eta_min": avg_historical_eta_min,
            "num_past_trips": num_past_trips,
            "on_time_ratio": on_time_ratio,
            "eta_min": eta_min,
        }
    )
    return df


def train_eta_model(n_rows: int = 5000) -> None:
    df = generate_synthetic_telemetry(n_rows)
    df.to_csv(DATA_DIR / "synthetic_trips.csv", index=False)

    feature_cols = [
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
    X = df[feature_cols]
    y = df["eta_min"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        random_state=42,
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"[ETA MODEL] MAE on test set: {mae:.2f} minutes")

    model_path = ML_DIR / "eta_model.joblib"
    joblib.dump(model, model_path)
    print(f"[ETA MODEL] Saved model to {model_path}")


if __name__ == "__main__":
    train_eta_model()