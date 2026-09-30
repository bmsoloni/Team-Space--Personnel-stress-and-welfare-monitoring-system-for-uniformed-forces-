from ..extensions import db
from datetime import datetime

class DutySchedule(db.Model):
    __tablename__ = "duty_schedules"
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey("personnel.id"), nullable=False, index=True)
    week_start = db.Column(db.Date, nullable=False)
    duty_hours = db.Column(db.Float, default=0)
    overtime_hours = db.Column(db.Float, default=0)
    night_shifts = db.Column(db.Integer, default=0)
    total_shifts = db.Column(db.Integer, default=0)
    consecutive_duty_days = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "personnel_id": self.personnel_id,
            "week_start": str(self.week_start), "duty_hours": self.duty_hours,
            "overtime_hours": self.overtime_hours, "night_shifts": self.night_shifts,
            "total_shifts": self.total_shifts,
            "consecutive_duty_days": self.consecutive_duty_days,
        }
