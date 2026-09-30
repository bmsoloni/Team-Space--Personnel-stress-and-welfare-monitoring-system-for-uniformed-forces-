from ..extensions import db
from datetime import datetime

class DeploymentRecord(db.Model):
    __tablename__ = "deployment_records"
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey("personnel.id"), nullable=False, index=True)
    location = db.Column(db.String(200), nullable=False)
    zone = db.Column(db.Enum("peace","field","high_altitude","insurgency","counter_terror"), default="peace")
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    duration_days = db.Column(db.Integer, nullable=True)
    is_current = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "personnel_id": self.personnel_id,
            "location": self.location, "zone": self.zone,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date) if self.end_date else None,
            "duration_days": self.duration_days, "is_current": self.is_current,
        }
