from datetime import date
from ..extensions import db
from ..models.risk_score import RiskScore
from ..models.alert import Alert
from ..models.personnel import Personnel
from ..ai.feature_engineering import build_feature_vector, get_feature_array
from ..ai.model_registry import predict_stress, predict_burnout, detect_anomaly
from ..ai.explainability import get_shap_explanation
from ..utils.constants import RiskLevel

def get_risk_level(score: float) -> str:
    if score < 40: return RiskLevel.LOW
    if score < 60: return RiskLevel.MODERATE
    if score < 80: return RiskLevel.HIGH
    return RiskLevel.CRITICAL

def compute_risk_for_personnel(personnel_id: int) -> RiskScore:
    features = build_feature_vector(personnel_id)
    if not features:
        return None
    X = get_feature_array(features)
    stress = predict_stress(X)
    burnout = predict_burnout(X)
    is_anomaly = detect_anomaly(X)
    overall = max(stress, burnout)
    risk_level = get_risk_level(overall)
    explanation = get_shap_explanation(features, stress, burnout)
    explanation["recommended_actions"] = _get_recommendations(risk_level, features)
    score = RiskScore(
        personnel_id=personnel_id,
        score_date=date.today(),
        stress_score=stress,
        burnout_score=burnout,
        overall_risk=risk_level,
        risk_factors=explanation,
        is_anomaly=is_anomaly,
        model_version="v1.0",
    )
    db.session.add(score)
    db.session.commit()
    if risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
        _create_alert(personnel_id, risk_level, stress)
    return score

def _create_alert(personnel_id, risk_level, score):
    existing = Alert.query.filter_by(personnel_id=personnel_id, status="OPEN").first()
    if existing:
        return
    severity = "URGENT" if risk_level == RiskLevel.CRITICAL else "HIGH"
    alert = Alert(
        personnel_id=personnel_id, alert_type="HIGH_STRESS",
        severity=severity, status="OPEN",
    )
    db.session.add(alert)
    db.session.commit()

def _get_recommendations(risk_level, features):
    recs = []
    if risk_level in ("HIGH","CRITICAL"):
        recs.append("Schedule welfare counseling within 7 days")
    if features.get("leave_denied_90d", 0) >= 2:
        recs.append("Consider approving pending leave request")
    if features.get("deployment_duration_days", 0) > 270:
        recs.append("Evaluate transfer/rotation per policy guidelines")
    if features.get("consecutive_duty_days", 0) > 21:
        recs.append("Mandate rest days — consecutive duty exceeds safe limits")
    if features.get("wellness_score_avg", 100) < 40:
        recs.append("Refer to medical officer for wellness evaluation")
    return recs if recs else ["Monitor situation and reassess in 7 days"]

def run_batch_risk_calculation():
    """Called by APScheduler daily at 2:00 AM."""
    personnel = Personnel.query.filter_by(is_active=True).all()
    count = 0
    for p in personnel:
        try:
            compute_risk_for_personnel(p.id)
            count += 1
        except Exception as e:
            print(f"[Risk] Error for personnel {p.id}: {e}")
    print(f"[Risk] Batch complete: {count}/{len(personnel)} scored")
    return count
