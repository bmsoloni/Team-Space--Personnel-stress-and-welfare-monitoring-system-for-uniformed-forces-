from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.personnel import Personnel
from ..models.risk_score import RiskScore
from ..middleware.rbac import welfare_or_admin, commander_or_above
from ..middleware.audit import audit_log
from ..services.risk_service import compute_risk_for_personnel
from sqlalchemy import desc, func
from datetime import date, timedelta

risk_bp = Blueprint("risk", __name__)

@risk_bp.route("/scores", methods=["GET"])
@jwt_required()
@commander_or_above
def all_scores():
    risk_level = request.args.get("risk")
    unit_id = request.args.get("unit_id")
    subq = (RiskScore.query
        .with_entities(RiskScore.personnel_id, func.max(RiskScore.score_date).label("max_date"))
        .group_by(RiskScore.personnel_id).subquery())
    query = (RiskScore.query
        .join(subq, (RiskScore.personnel_id == subq.c.personnel_id) & (RiskScore.score_date == subq.c.max_date)))
    if risk_level:
        query = query.filter(RiskScore.overall_risk == risk_level)
    scores = query.all()
    return jsonify([s.to_dict() for s in scores]), 200

@risk_bp.route("/<int:personnel_id>", methods=["GET"])
@jwt_required()
@welfare_or_admin
@audit_log("VIEW_RISK_SCORE", "risk_scores")
def get_latest(personnel_id):
    Personnel.query.get_or_404(personnel_id)
    score = RiskScore.query.filter_by(personnel_id=personnel_id).order_by(desc(RiskScore.score_date)).first()
    if not score:
        return jsonify({"message": "No risk score found", "risk": "NOT_ASSESSED"}), 200
    return jsonify(score.to_dict()), 200

@risk_bp.route("/<int:personnel_id>/history", methods=["GET"])
@jwt_required()
@welfare_or_admin
def history(personnel_id):
    days = int(request.args.get("days", 90))
    since = date.today() - timedelta(days=days)
    scores = (RiskScore.query
        .filter(RiskScore.personnel_id == personnel_id, RiskScore.score_date >= since)
        .order_by(RiskScore.score_date).all())
    return jsonify([s.to_dict() for s in scores]), 200

@risk_bp.route("/trigger/<int:personnel_id>", methods=["POST"])
@jwt_required()
@welfare_or_admin
def trigger_analysis(personnel_id):
    Personnel.query.get_or_404(personnel_id)
    score = compute_risk_for_personnel(personnel_id)
    if not score:
        return jsonify({"error": "Could not compute risk score"}), 500
    return jsonify({"message": "Risk analysis complete", "score": score.to_dict()}), 200

@risk_bp.route("/heatmap", methods=["GET"])
@jwt_required()
@commander_or_above
def heatmap():
    subq = (RiskScore.query
        .with_entities(RiskScore.personnel_id, func.max(RiskScore.score_date).label("max_date"))
        .group_by(RiskScore.personnel_id).subquery())
    latest = (RiskScore.query
        .join(subq, (RiskScore.personnel_id == subq.c.personnel_id) & (RiskScore.score_date == subq.c.max_date))
        .all())
    result = {}
    for score in latest:
        p = Personnel.query.get(score.personnel_id)
        if not p: continue
        unit = p.unit_name or f"Unit-{p.unit_id}"
        if unit not in result:
            result[unit] = {"LOW":0,"MODERATE":0,"HIGH":0,"CRITICAL":0,"total":0}
        result[unit][score.overall_risk] += 1
        result[unit]["total"] += 1
    return jsonify(result), 200

@risk_bp.route("/explain/<int:personnel_id>", methods=["GET"])
@jwt_required()
@welfare_or_admin
@audit_log("VIEW_SHAP_EXPLANATION", "risk_scores")
def explain(personnel_id):
    score = RiskScore.query.filter_by(personnel_id=personnel_id).order_by(desc(RiskScore.score_date)).first()
    if not score:
        return jsonify({"error": "No score found"}), 404
    return jsonify({
        "personnel_id": personnel_id,
        "stress_score": score.stress_score,
        "burnout_score": score.burnout_score,
        "overall_risk": score.overall_risk,
        "explanation": score.risk_factors,
        "is_anomaly": score.is_anomaly,
    }), 200
