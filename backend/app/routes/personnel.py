from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db, bcrypt
from ..models.personnel import Personnel
from ..models.leave_record import LeaveRecord
from ..models.deployment_record import DeploymentRecord
from ..models.risk_score import RiskScore
from ..middleware.rbac import welfare_or_admin, admin_only
from ..middleware.audit import audit_log
from ..utils.pagination import get_pagination_params, paginate_query
from sqlalchemy import desc

personnel_bp = Blueprint("personnel", __name__)

@personnel_bp.route("/", methods=["GET"])
@jwt_required()
@welfare_or_admin
def get_all():
    page, per_page = get_pagination_params()
    q = request.args.get("q", "")
    zone = request.args.get("zone", "")
    risk = request.args.get("risk", "")

    query = Personnel.query.filter_by(is_active=True)
    if zone:
        query = query.filter_by(deployment_zone=zone)

    paginated = paginate_query(query.order_by(Personnel.id), page, per_page)
    items = []
    for p in paginated["items"]:
        d = p.to_dict(include_pii=True)
        latest = RiskScore.query.filter_by(personnel_id=p.id).order_by(desc(RiskScore.score_date)).first()
        d["latest_risk"] = latest.overall_risk if latest else "NOT_ASSESSED"
        d["stress_score"] = latest.stress_score if latest else None
        items.append(d)

    if risk:
        items = [i for i in items if i.get("latest_risk") == risk]

    paginated["items"] = items
    return jsonify(paginated), 200

@personnel_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
@welfare_or_admin
@audit_log("VIEW_PROFILE", "personnel")
def get_one(id):
    p = Personnel.query.get_or_404(id)
    data = p.to_dict(include_pii=True)
    latest = RiskScore.query.filter_by(personnel_id=id).order_by(desc(RiskScore.score_date)).first()
    data["latest_risk_score"] = latest.to_dict() if latest else None
    return jsonify(data), 200

@personnel_bp.route("/<int:id>/risk-timeline", methods=["GET"])
@jwt_required()
@welfare_or_admin
def risk_timeline(id):
    Personnel.query.get_or_404(id)
    days = int(request.args.get("days", 90))
    from datetime import date, timedelta
    since = date.today() - timedelta(days=days)
    scores = RiskScore.query.filter(
        RiskScore.personnel_id == id,
        RiskScore.score_date >= since
    ).order_by(RiskScore.score_date).all()
    return jsonify([s.to_dict() for s in scores]), 200

@personnel_bp.route("/<int:id>/leaves", methods=["GET"])
@jwt_required()
@welfare_or_admin
def leaves(id):
    Personnel.query.get_or_404(id)
    records = LeaveRecord.query.filter_by(personnel_id=id).order_by(desc(LeaveRecord.applied_at)).all()
    return jsonify([r.to_dict() for r in records]), 200

@personnel_bp.route("/<int:id>/deployments", methods=["GET"])
@jwt_required()
@welfare_or_admin
def deployments(id):
    Personnel.query.get_or_404(id)
    records = DeploymentRecord.query.filter_by(personnel_id=id).order_by(desc(DeploymentRecord.start_date)).all()
    return jsonify([r.to_dict() for r in records]), 200

@personnel_bp.route("/", methods=["POST"])
@jwt_required()
@welfare_or_admin
def create():
    data = request.get_json()
    p = Personnel()
    p.name = data["name"]
    p.service_number = data["service_number"]
    p.unit_id = data.get("unit_id")
    p.unit_name = data.get("unit_name")
    p.rank = data.get("rank")
    p.years_of_service = data.get("years_of_service", 0)
    p.deployment_zone = data.get("deployment_zone", "peace")
    p.family_station = data.get("family_station", False)
    db.session.add(p)
    db.session.commit()
    
    # Automatically compute risk score for the new officer
    try:
        from ..services.risk_service import compute_risk_for_personnel
        compute_risk_for_personnel(p.id)
    except Exception as e:
        print(f"Failed to auto-compute risk score: {e}")

    return jsonify(p.to_dict(include_pii=True)), 201

@personnel_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@welfare_or_admin
def update(id):
    p = Personnel.query.get_or_404(id)
    data = request.get_json()
    for field in ["rank","unit_id","unit_name","years_of_service","deployment_zone","family_station"]:
        if field in data:
            setattr(p, field, data[field])
    if "name" in data: p.name = data["name"]
    if "service_number" in data: p.service_number = data["service_number"]
    db.session.commit()
    return jsonify(p.to_dict(include_pii=True)), 200

@personnel_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@welfare_or_admin
def delete_personnel(id):
    p = Personnel.query.get_or_404(id)
    # Soft delete to preserve historical records, or hard delete if requested
    hard = request.args.get("hard", "false").lower() == "true"
    if hard:
        # Delete related child records first to satisfy foreign keys
        from ..models.alert import Alert
        from ..models.risk_score import RiskScore
        from ..models.leave_record import LeaveRecord
        from ..models.deployment_record import DeploymentRecord
        Alert.query.filter_by(personnel_id=id).delete()
        RiskScore.query.filter_by(personnel_id=id).delete()
        LeaveRecord.query.filter_by(personnel_id=id).delete()
        DeploymentRecord.query.filter_by(personnel_id=id).delete()
        db.session.delete(p)
    else:
        p.is_active = False
    db.session.commit()
    return jsonify({"message": f"Personnel #{id} successfully {'deleted' if hard else 'deactivated'}"}), 200

