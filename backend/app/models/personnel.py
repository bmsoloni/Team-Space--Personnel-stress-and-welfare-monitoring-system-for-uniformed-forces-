from ..extensions import db
from ..utils.encryption import encrypt_field, decrypt_field
from datetime import datetime
import uuid

class Personnel(db.Model):
    __tablename__ = "personnel"
    id = db.Column(db.Integer, primary_key=True)
    anon_id = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    _service_number = db.Column("service_number", db.Text, nullable=False)
    _name = db.Column("name", db.Text, nullable=False)
    unit_id = db.Column(db.Integer, nullable=True)
    unit_name = db.Column(db.String(100), nullable=True)
    
    rank = db.Column('rank', db.String(50), nullable=True)
    years_of_service = db.Column(db.Integer, default=0)
    deployment_zone = db.Column(db.Enum("peace","field","high_altitude","insurgency","counter_terror"), default="peace")
    family_station = db.Column(db.Boolean, default=False)
    date_of_joining = db.Column(db.Date, nullable=True)
    current_posting_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    leave_records = db.relationship("LeaveRecord", backref="personnel", lazy=True)
    deployment_records = db.relationship("DeploymentRecord", backref="personnel", lazy=True)
    risk_scores = db.relationship("RiskScore", backref="personnel", lazy=True)
    alerts = db.relationship("Alert", backref="personnel", lazy=True)
    wellness_assessments = db.relationship("WellnessAssessment", backref="personnel", lazy=True)

    @property
    def service_number(self):
        return decrypt_field(self._service_number)

    @service_number.setter
    def service_number(self, value):
        self._service_number = encrypt_field(value)

    @property
    def name(self):
        return decrypt_field(self._name)

    @name.setter
    def name(self, value):
        self._name = encrypt_field(value)

    def to_dict(self, include_pii=False):
        data = {
            "id": self.id,
            "anon_id": self.anon_id,
            "unit_id": self.unit_id,
            "unit_name": self.unit_name,
            "rank": self.rank,
            "years_of_service": self.years_of_service,
            "deployment_zone": self.deployment_zone,
            "family_station": self.family_station,
            "date_of_joining": self.date_of_joining.isoformat() if self.date_of_joining else None,
            "current_posting_date": self.current_posting_date.isoformat() if self.current_posting_date else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }
        if include_pii:
            data["name"] = self.name
            data["service_number"] = self.service_number
        return data

