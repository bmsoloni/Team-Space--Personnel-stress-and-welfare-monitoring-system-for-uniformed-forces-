from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..extensions import db, bcrypt
from ..models.user import User
from ..models.audit_log import AuditLog
from ..middleware.rbac import admin_only
from sqlalchemy import desc

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_only
def list_users():
    users = User.query.order_by(desc(User.created_at)).all()
    return jsonify([u.to_dict() for u in users]), 200

@admin_bp.route("/users", methods=["POST"])
@jwt_required()
@admin_only
def create_user():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409
    from ..extensions import bcrypt as bc
    user = User(
        email=data["email"],
        password_hash=bc.generate_password_hash(data["password"]).decode("utf-8"),
        full_name=data["full_name"], role=data["role"],
        unit_id=data.get("unit_id"),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@admin_bp.route("/users/<int:id>", methods=["PUT"])
@jwt_required()
@admin_only
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    for f in ["full_name","role","unit_id","is_active"]:
        if f in data: setattr(user, f, data[f])
    db.session.commit()
    return jsonify(user.to_dict()), 200

@admin_bp.route("/audit-logs", methods=["GET"])
@jwt_required()
@admin_only
def audit_logs():
    logs = AuditLog.query.order_by(desc(AuditLog.timestamp)).limit(200).all()
    return jsonify([l.to_dict() for l in logs]), 200

@admin_bp.route("/system-health", methods=["GET"])
@jwt_required()
@admin_only
def system_health():
    from ..models.risk_score import RiskScore
    from ..models.personnel import Personnel
    return jsonify({
        "status": "healthy",
        "total_personnel": Personnel.query.count(),
        "total_risk_scores": RiskScore.query.count(),
        "db": "connected",
    }), 200


@admin_bp.route("/users/<int:id>", methods=["DELETE"])
@jwt_required()
@admin_only
def delete_user(id):
    user = User.query.get_or_404(id)
    hard = request.args.get("hard", "false").lower() == "true"
    if hard:
        db.session.delete(user)
    else:
        user.is_active = False
    db.session.commit()
    return jsonify({"message": f"User #{id} ({user.email}) successfully {'deleted' if hard else 'deactivated'}"}), 200
