from ..extensions import db
from datetime import datetime

class WellnessAssessment(db.Model):
    __tablename__ = "wellness_assessments"
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey("personnel.id"), nullable=False, index=True)
    score = db.Column(db.Float, nullable=False)  # 0-100
    mood_score = db.Column(db.Integer, nullable=True)       # 1-10
    sleep_quality = db.Column(db.Integer, nullable=True)    # 1-10
    energy_level = db.Column(db.Integer, nullable=True)     # 1-10
    stress_level = db.Column(db.Integer, nullable=True)     # 1-10
    social_support = db.Column(db.Integer, nullable=True)   # 1-10
    responses = db.Column(db.JSON, nullable=True)
    consent_given = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "personnel_id": self.personnel_id,
            "score": self.score, "mood_score": self.mood_score,
            "sleep_quality": self.sleep_quality, "energy_level": self.energy_level,
            "stress_level": self.stress_level, "social_support": self.social_support,
            "submitted_at": self.submitted_at.isoformat(),
        }
