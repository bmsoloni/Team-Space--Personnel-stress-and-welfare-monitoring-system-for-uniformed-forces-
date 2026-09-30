from ..extensions import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False)
    target_table = db.Column(db.String(50), nullable=True)
    target_id = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    extra_data = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id, "user_id": self.user_id, "action": self.action,
            "target_table": self.target_table, "target_id": self.target_id,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat(),
        }
