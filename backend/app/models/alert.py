from ..extensions import db
from datetime import datetime

class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey("personnel.id"), nullable=False, index=True)
    alert_type = db.Column(db.Enum("HIGH_STRESS","BURNOUT","ANOMALY","SELF_REPORT","MANUAL"), nullable=False)
    severity = db.Column(db.Enum("LOW","MEDIUM","HIGH","URGENT"), nullable=False)
    status = db.Column(db.Enum("OPEN","ACKNOWLEDGED","RESOLVED","ESCALATED"), default="OPEN", index=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    assignee = db.relationship("User", foreign_keys=[assigned_to])

    def to_dict(self):
        return {
            "id": self.id, "personnel_id": self.personnel_id,
            "alert_type": self.alert_type, "severity": self.severity,
            "status": self.status, "assigned_to": self.assigned_to,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }
