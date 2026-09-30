import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.personnel import Personnel
from app.models.risk_score import RiskScore
from app.services.risk_service import compute_risk_for_personnel

app = create_app()

def evaluate_missing():
    with app.app_context():
        officers = Personnel.query.all()
        for o in officers:
            score = RiskScore.query.filter_by(personnel_id=o.id).first()
            if not score:
                print(f"Computing risk for unassessed officer: {o.name}")
                compute_risk_for_personnel(o.id)

if __name__ == '__main__':
    evaluate_missing()
