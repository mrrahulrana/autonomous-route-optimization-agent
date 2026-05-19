from app.ml.predict_eta import predict_eta

def test_predict_eta_returns_positive_eta():
    trips = [
        {
            "origin": 1,
            "destination": 10,
            "distance_km": 15.0,
            "time_of_day": 8,
            "day_of_week": 2,
            "traffic_level": 1,
        }
    ]

    preds = predict_eta(trips)

    # We expect exactly one prediction
    assert len(preds) == 1

    # ETA should be positive (minutes)
    assert preds[0] > 0