import joblib, os
import numpy as np

_models = {}
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../../ml_models")

def load_models():
    global _models
    try:
        _models["stress"] = joblib.load(os.path.join(MODEL_DIR, "stress_model_v1.pkl"))
        _models["burnout"] = joblib.load(os.path.join(MODEL_DIR, "burnout_model_v1.pkl"))
        _models["anomaly"] = joblib.load(os.path.join(MODEL_DIR, "anomaly_detector_v1.pkl"))
        _models["scaler"] = joblib.load(os.path.join(MODEL_DIR, "scaler_v1.pkl"))
        print("[AI] Models loaded successfully")
    except FileNotFoundError:
        print("[AI] WARNING: Model files not found. Run training/train_stress_model.py first.")

def get_model(name):
    if not _models:
        load_models()
    return _models.get(name)

def predict_stress(X: np.ndarray) -> float:
    model = get_model("stress")
    scaler = get_model("scaler")
    if model is None:
        return _rule_based_stress(X)
    Xs = scaler.transform(X) if scaler else X
    proba = model.predict_proba(Xs)[0]
    # Convert class probabilities to 0-100 score
    score = proba[-1] * 100 if len(proba) > 1 else float(model.predict(Xs)[0]) * 100
    return round(min(max(score, 0), 100), 2)

def predict_burnout(X: np.ndarray) -> float:
    model = get_model("burnout")
    scaler = get_model("scaler")
    if model is None:
        return _rule_based_burnout(X)
    Xs = scaler.transform(X) if scaler else X
    proba = model.predict_proba(Xs)[0]
    return round(min(max(proba[-1] * 100, 0), 100), 2)

def detect_anomaly(X: np.ndarray) -> bool:
    model = get_model("anomaly")
    if model is None:
        return False
    pred = model.predict(X)
    return bool(pred[0] == -1)

def _rule_based_stress(X: np.ndarray) -> float:
    """Fallback rule-based scoring when models are not trained yet."""
    x = X[0]
    score = 20.0
    score += min(x[4] / 365 * 30, 30)   # deployment_duration_days
    score += x[1] * 5                    # leave_denied_90d
    score += min(x[6] * 1.5, 15)        # consecutive_duty_days
    score += max(0, (x[2] - 48) * 0.5) # overtime
    score -= (x[7] - 50) * 0.2          # wellness bonus
    score += x[12] * 20                 # zone_risk_factor
    return round(min(max(score, 0), 100), 2)

def _rule_based_burnout(X: np.ndarray) -> float:
    x = X[0]
    score = 15.0
    score += min(x[4] / 365 * 25, 25)
    score += x[3] * 3
    score -= (x[7] - 50) * 0.15
    score += x[11] * 20
    return round(min(max(score, 0), 100), 2)
