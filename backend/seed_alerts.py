import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.personnel import Personnel
from app.models.risk_score import RiskScore
from app.models.alert import Alert

app = create_app()

def generate_alerts():
    with app.app_context():
        Alert.query.delete()
        officers = Personnel.query.all()
        
        alerts_created = 0
        for o in officers:
            # get latest risk score
            rs = RiskScore.query.filter_by(personnel_id=o.id).order_by(RiskScore.score_date.desc()).first()
            if rs and rs.overall_risk in ["HIGH", "CRITICAL"]:
                alert = Alert()
                alert.personnel_id = o.id
                alert.alert_type = "HIGH_STRESS" if rs.stress_score > rs.burnout_score else "BURNOUT"
                alert.severity = "URGENT" if rs.overall_risk == "CRITICAL" else "HIGH"
                alert.status = "OPEN"
                alert.notes = "Automatically generated alert due to risk score threshold"
                db.session.add(alert)
                alerts_created += 1
                
        db.session.commit()
        print(f"Successfully generated {alerts_created} alerts based on high risk scores.")

if __name__ == '__main__':
    generate_alerts()
