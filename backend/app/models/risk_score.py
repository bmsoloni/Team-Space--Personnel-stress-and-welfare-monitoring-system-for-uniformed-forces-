from ..extensions import db
from datetime import datetime

class RiskScore(db.Model):
    __tablename__ = "risk_scores"
    id = db.Column(db.Integer, primary_key=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey("personnel.id"), nullable=False, index=True)
    score_date = db.Column(db.Date, nullable=False, index=True)
    stress_score = db.Column(db.Float, default=0.0)
    burnout_score = db.Column(db.Float, default=0.0)
    overall_risk = db.Column(db.Enum("LOW","MODERATE","HIGH","CRITICAL"), default="LOW")
    risk_factors = db.Column(db.JSON, nullable=True)
    model_version = db.Column(db.String(20), default="v1.0")
    is_anomaly = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "personnel_id": self.personnel_id,
            "score_date": str(self.score_date),
            "stress_score": self.stress_score,
            "burnout_score": self.burnout_score,
            "overall_risk": self.overall_risk,
            "risk_factors": self.risk_factors,
            "model_version": self.model_version,
            "is_anomaly": self.is_anomaly,
            "created_at": self.created_at.isoformat(),
        }
