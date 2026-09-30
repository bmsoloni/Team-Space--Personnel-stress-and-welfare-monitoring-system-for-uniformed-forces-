from datetime import datetime, timedelta
from ..models.alert import Alert
from ..extensions import db

def run_alert_escalation():
    threshold = datetime.utcnow() - timedelta(hours=48)
    stale = Alert.query.filter(
        Alert.status == "OPEN",
        Alert.created_at <= threshold
    ).all()
    for alert in stale:
        alert.status = "ESCALATED"
    if stale:
        db.session.commit()
    print(f"[Job] Escalated {len(stale)} stale alerts")
