from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.alert import Alert
from ..middleware.rbac import welfare_or_admin, commander_or_above
from ..middleware.audit import audit_log
from datetime import datetime
from sqlalchemy import desc

alerts_bp = Blueprint("alerts", __name__)

@alerts_bp.route("/", methods=["GET"])
@jwt_required()
@commander_or_above
def get_all():
    status = request.args.get("status")
    severity = request.args.get("severity")
    query = Alert.query
    if status:
        query = query.filter_by(status=status)
    if severity:
        query = query.filter_by(severity=severity)
    alerts = query.order_by(desc(Alert.created_at)).limit(100).all()
    return jsonify([a.to_dict() for a in alerts]), 200

@alerts_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
@welfare_or_admin
def get_one(id):
    alert = Alert.query.get_or_404(id)
    return jsonify(alert.to_dict()), 200

@alerts_bp.route("/<int:id>/acknowledge", methods=["PATCH"])
@jwt_required()
@welfare_or_admin
@audit_log("ACKNOWLEDGE_ALERT", "alerts")
def acknowledge(id):
    alert = Alert.query.get_or_404(id)
    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Alert acknowledged", "alert": alert.to_dict()}), 200

@alerts_bp.route("/<int:id>/resolve", methods=["PATCH"])
@jwt_required()
@welfare_or_admin
@audit_log("RESOLVE_ALERT", "alerts")
def resolve(id):
    alert = Alert.query.get_or_404(id)
    data = request.get_json() or {}
    alert.status = "RESOLVED"
    alert.resolved_at = datetime.utcnow()
    alert.notes = data.get("notes", alert.notes)
    db.session.commit()
    return jsonify({"message": "Alert resolved", "alert": alert.to_dict()}), 200

@alerts_bp.route("/<int:id>/escalate", methods=["POST"])
@jwt_required()
@welfare_or_admin
@audit_log("ESCALATE_ALERT", "alerts")
def escalate(id):
    alert = Alert.query.get_or_404(id)
    alert.status = "ESCALATED"
    db.session.commit()
    return jsonify({"message": "Alert escalated", "alert": alert.to_dict()}), 200

@alerts_bp.route("/manual", methods=["POST"])
@jwt_required()
@welfare_or_admin
def create_manual():
    data = request.get_json()
    alert = Alert(
        personnel_id=data["personnel_id"], alert_type="MANUAL",
        severity=data.get("severity", "MEDIUM"),
        notes=data.get("notes", ""), assigned_to=get_jwt_identity(),
    )
    db.session.add(alert)
    db.session.commit()
    return jsonify(alert.to_dict()), 201
