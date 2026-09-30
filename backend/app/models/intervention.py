from ..extensions import db
from datetime import datetime

class Intervention(db.Model):
    __tablename__ = "interventions"
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey("personnel.id"), nullable=False)
    alert_id = db.Column(db.Integer, db.ForeignKey("alerts.id"), nullable=True)
    officer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    intervention_type = db.Column(db.Enum("counseling","leave_approved","workload_reduced","medical_referral","family_support","other"), nullable=False)
    description = db.Column(db.Text, nullable=True)
    outcome = db.Column(db.Text, nullable=True)
    follow_up_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "personnel_id": self.personnel_id,
            "alert_id": self.alert_id, "officer_id": self.officer_id,
            "intervention_type": self.intervention_type,
            "description": self.description, "outcome": self.outcome,
            "follow_up_date": str(self.follow_up_date) if self.follow_up_date else None,
            "created_at": self.created_at.isoformat(),
        }
