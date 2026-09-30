class RiskLevel:
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertType:
    HIGH_STRESS = "HIGH_STRESS"
    BURNOUT = "BURNOUT"
    ANOMALY = "ANOMALY"
    SELF_REPORT = "SELF_REPORT"
    MANUAL = "MANUAL"

class AlertStatus:
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"

class AlertSeverity:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class UserRole:
    SUPER_ADMIN = "super_admin"
    WELFARE_OFFICER = "welfare_officer"
    COMMANDER = "commander"
    MEDICAL_OFFICER = "medical_officer"
    PERSONNEL = "personnel"

class DeploymentZone:
    PEACE = "peace"
    FIELD = "field"
    HIGH_ALTITUDE = "high_altitude"
    INSURGENCY = "insurgency"
    COUNTER_TERROR = "counter_terror"

RISK_THRESHOLDS = {
    "LOW": (0, 40),
    "MODERATE": (40, 60),
    "HIGH": (60, 80),
    "CRITICAL": (80, 100),
}
