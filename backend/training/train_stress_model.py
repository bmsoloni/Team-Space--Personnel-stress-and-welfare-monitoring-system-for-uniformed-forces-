"""Train and save the stress risk and burnout models."""
import pandas as pd
import numpy as np
import joblib, os
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
try:
    from xgboost import XGBClassifier
    USE_XGB = True
except ImportError:
    USE_XGB = False

MODEL_DIR = os.path.join(os.path.dirname(__file__), "../ml_models")
os.makedirs(MODEL_DIR, exist_ok=True)
DATA_FILE = os.path.join(os.path.dirname(__file__), "synthetic_training_data.csv")

FEATURES = ["leave_frequency_30d","leave_denied_90d","avg_duty_hours_weekly","overtime_days_30d",
            "deployment_duration_days","transfer_count_2yr","consecutive_duty_days","wellness_score_avg",
            "family_separation_days","incident_exposure_count","training_burden_days","night_shift_ratio",
            "zone_risk_factor","years_of_service"]

def train():
    if not os.path.exists(DATA_FILE):
        print("Generating synthetic data first...")
        import subprocess
        subprocess.run(["python", "synthetic_data_generator.py"], cwd=os.path.dirname(__file__))

    df = pd.read_csv(DATA_FILE)
    X = df[FEATURES].values
    y_stress = df["stress_label"].values
    y_burnout = df["burnout_label"].values

    X_tr, X_te, ys_tr, ys_te, yb_tr, yb_te = train_test_split(X, y_stress, y_burnout, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)

    # Stress model
    print("Training stress model...")
    if USE_XGB:
        stress_model = XGBClassifier(n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42, eval_metric="logloss")
    else:
        stress_model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)
    stress_model.fit(X_tr_s, ys_tr)
    print("Stress model:\n", classification_report(ys_te, stress_model.predict(X_te_s)))

    # Burnout model
    print("Training burnout model...")
    burnout_model = RandomForestClassifier(n_estimators=150, max_depth=7, random_state=42, n_jobs=-1)
    burnout_model.fit(X_tr_s, yb_tr)
    print("Burnout model:\n", classification_report(yb_te, burnout_model.predict(X_te_s)))

    # Anomaly detector
    anomaly_model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    anomaly_model.fit(X_tr_s)

    # Save
    joblib.dump(stress_model, os.path.join(MODEL_DIR, "stress_model_v1.pkl"))
    joblib.dump(burnout_model, os.path.join(MODEL_DIR, "burnout_model_v1.pkl"))
    joblib.dump(anomaly_model, os.path.join(MODEL_DIR, "anomaly_detector_v1.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler_v1.pkl"))
    print(f"\n✅ All models saved to {MODEL_DIR}")

if __name__ == "__main__":
    train()
