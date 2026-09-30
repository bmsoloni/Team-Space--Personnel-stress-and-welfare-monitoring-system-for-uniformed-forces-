from ..extensions import db
from datetime import datetime

class LeaveRecord(db.Model):
    __tablename__ = "leave_records"
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey("personnel.id"), nullable=False, index=True)
    leave_type = db.Column(db.Enum("annual","casual","medical","emergency","special"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum("approved","pending","denied","cancelled"), default="pending")
    reason = db.Column(db.Text, nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "personnel_id": self.personnel_id,
            "leave_type": self.leave_type, "start_date": str(self.start_date),
            "end_date": str(self.end_date), "days": self.days,
            "status": self.status, "reason": self.reason,
            "applied_at": self.applied_at.isoformat(),
        }
