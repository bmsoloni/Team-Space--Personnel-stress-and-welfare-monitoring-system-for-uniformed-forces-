import numpy as np
from datetime import date, timedelta
from ..models.leave_record import LeaveRecord
from ..models.deployment_record import DeploymentRecord
from ..models.duty_schedule import DutySchedule
from ..models.wellness_assessment import WellnessAssessment
from ..models.personnel import Personnel

def build_feature_vector(personnel_id: int) -> dict:
    """Extract HR features from MySQL for a given personnel (by personnel_id).
    Returns anonymized numerical features — no PII."""
    today = date.today()
    p = Personnel.query.get(personnel_id)
    if not p:
        return None

    # Leave features
    last_30 = today - timedelta(days=30)
    last_90 = today - timedelta(days=90)
    leaves_30 = LeaveRecord.query.filter(
        LeaveRecord.personnel_id == personnel_id,
        LeaveRecord.start_date >= last_30,
        LeaveRecord.status == "approved"
    ).count()
    denied_90 = LeaveRecord.query.filter(
        LeaveRecord.personnel_id == personnel_id,
        LeaveRecord.applied_at >= last_90,
        LeaveRecord.status == "denied"
    ).count()

    # Deployment features
    current_dep = DeploymentRecord.query.filter_by(personnel_id=personnel_id, is_current=True).first()
    deployment_days = 0
    if current_dep:
        deployment_days = (today - current_dep.start_date).days

    transfers_2yr = DeploymentRecord.query.filter(
        DeploymentRecord.personnel_id == personnel_id,
        DeploymentRecord.start_date >= today - timedelta(days=730)
    ).count()

    # Duty features (last 8 weeks)
    last_8w = today - timedelta(weeks=8)
    schedules = DutySchedule.query.filter(
        DutySchedule.personnel_id == personnel_id,
        DutySchedule.week_start >= last_8w
    ).all()
    avg_duty_hours = np.mean([s.duty_hours for s in schedules]) if schedules else 40.0
    overtime_days = sum(1 for s in schedules if s.overtime_hours > 0)
    night_shifts = sum(s.night_shifts for s in schedules)
    total_shifts = sum(s.total_shifts for s in schedules) or 1
    night_ratio = night_shifts / total_shifts
    max_consec = max((s.consecutive_duty_days for s in schedules), default=0)

    # Wellness features
    last_3 = WellnessAssessment.query.filter_by(personnel_id=personnel_id).order_by(
        WellnessAssessment.submitted_at.desc()
    ).limit(3).all()
    wellness_avg = np.mean([w.score for w in last_3]) if last_3 else 50.0

    # Zone risk multiplier
    zone_risk = {
        "peace": 0.2, "field": 0.5, "high_altitude": 0.7,
        "insurgency": 0.85, "counter_terror": 1.0
    }.get(p.deployment_zone, 0.3)

    return {
        "personnel_id": personnel_id,
        "anon_id": p.anon_id,
        "leave_frequency_30d": leaves_30,
        "leave_denied_90d": denied_90,
        "avg_duty_hours_weekly": round(float(avg_duty_hours), 2),
        "overtime_days_30d": overtime_days,
        "deployment_duration_days": deployment_days,
        "transfer_count_2yr": transfers_2yr,
        "consecutive_duty_days": max_consec,
        "wellness_score_avg": round(float(wellness_avg), 2),
        "family_separation_days": 0 if p.family_station else deployment_days,
        "incident_exposure_count": 0,
        "training_burden_days": 0,
        "night_shift_ratio": round(night_ratio, 3),
        "zone_risk_factor": zone_risk,
        "years_of_service": p.years_of_service or 0,
    }

def get_feature_array(features: dict) -> np.ndarray:
    """Convert feature dict to numpy array for model input."""
    keys = [
        "leave_frequency_30d", "leave_denied_90d", "avg_duty_hours_weekly",
        "overtime_days_30d", "deployment_duration_days", "transfer_count_2yr",
        "consecutive_duty_days", "wellness_score_avg", "family_separation_days",
        "incident_exposure_count", "training_burden_days", "night_shift_ratio",
        "zone_risk_factor", "years_of_service",
    ]
    return np.array([[features.get(k, 0) for k in keys]])
