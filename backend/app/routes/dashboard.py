from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models.risk_score import RiskScore
from ..models.alert import Alert
from ..models.personnel import Personnel
from ..middleware.rbac import commander_or_above, welfare_or_admin
from sqlalchemy import func, desc
from datetime import date, timedelta

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
@commander_or_above
def summary():
    total = Personnel.query.filter_by(is_active=True).count()
    subq = (RiskScore.query
        .with_entities(RiskScore.personnel_id, func.max(RiskScore.score_date).label("max_date"))
        .group_by(RiskScore.personnel_id).subquery())
    latest = (RiskScore.query
        .join(subq, (RiskScore.personnel_id == subq.c.personnel_id) & (RiskScore.score_date == subq.c.max_date))
        .all())
    risk_counts = {"LOW":0,"MODERATE":0,"HIGH":0,"CRITICAL":0}
    for s in latest:
        risk_counts[s.overall_risk] += 1
    open_alerts = Alert.query.filter_by(status="OPEN").count()
    urgent_alerts = Alert.query.filter(Alert.status.in_(["OPEN","ACKNOWLEDGED"]), Alert.severity=="URGENT").count()
    return jsonify({
        "total_personnel": total,
        "assessed_personnel": len(latest),
        "risk_distribution": risk_counts,
        "open_alerts": open_alerts,
        "urgent_alerts": urgent_alerts,
        "high_risk_count": risk_counts["HIGH"] + risk_counts["CRITICAL"],
    }), 200

@dashboard_bp.route("/trend", methods=["GET"])
@jwt_required()
@commander_or_above
def trend():
    days = int(request.args.get("days", 30))
    since = date.today() - timedelta(days=days)
    rows = (db.session.query(
            RiskScore.score_date,
            func.avg(RiskScore.stress_score).label("avg_stress"),
            func.avg(RiskScore.burnout_score).label("avg_burnout"),
            func.count(RiskScore.id).label("count"))
        .filter(RiskScore.score_date >= since)
        .group_by(RiskScore.score_date)
        .order_by(RiskScore.score_date).all())
    return jsonify([{
        "date": str(r.score_date),
        "avg_stress": round(float(r.avg_stress or 0), 2),
        "avg_burnout": round(float(r.avg_burnout or 0), 2),
        "count": r.count,
    } for r in rows]), 200

@dashboard_bp.route("/unit-breakdown", methods=["GET"])
@jwt_required()
@commander_or_above
def unit_breakdown():
    subq = (RiskScore.query
        .with_entities(RiskScore.personnel_id, func.max(RiskScore.score_date).label("max_date"))
        .group_by(RiskScore.personnel_id).subquery())
    latest = (RiskScore.query
        .join(subq, (RiskScore.personnel_id == subq.c.personnel_id) & (RiskScore.score_date == subq.c.max_date))
        .all())
    units = {}
    for score in latest:
        p = Personnel.query.get(score.personnel_id)
        if not p: continue
        unit = p.unit_name or f"Unit-{p.unit_id or 'Unknown'}"
        if unit not in units:
            units[unit] = {"unit": unit, "LOW":0,"MODERATE":0,"HIGH":0,"CRITICAL":0,"total":0,"avg_stress":0}
        units[unit][score.overall_risk] += 1
        units[unit]["total"] += 1
        units[unit]["avg_stress"] += score.stress_score
    for u in units.values():
        u["avg_stress"] = round(u["avg_stress"] / u["total"], 2) if u["total"] > 0 else 0
    return jsonify(list(units.values())), 200

@dashboard_bp.route("/alerts-overview", methods=["GET"])
@jwt_required()
@commander_or_above
def alerts_overview():
    statuses = ["OPEN","ACKNOWLEDGED","RESOLVED","ESCALATED"]
    data = {}
    for s in statuses:
        data[s] = Alert.query.filter_by(status=s).count()
    data["by_severity"] = {
        sv: Alert.query.filter_by(severity=sv).count()
        for sv in ["LOW","MEDIUM","HIGH","URGENT"]
    }
    return jsonify(data), 200

@dashboard_bp.route("/top-risk", methods=["GET"])
@jwt_required()
@welfare_or_admin
def top_risk():
    n = int(request.args.get("n", 10))
    subq = (RiskScore.query
        .with_entities(RiskScore.personnel_id, func.max(RiskScore.score_date).label("max_date"))
        .group_by(RiskScore.personnel_id).subquery())
    latest = (RiskScore.query
        .join(subq, (RiskScore.personnel_id == subq.c.personnel_id) & (RiskScore.score_date == subq.c.max_date))
        .filter(RiskScore.overall_risk.in_(["HIGH","CRITICAL"]))
        .order_by(desc(RiskScore.stress_score)).limit(n).all())
    result = []
    for s in latest:
        p = Personnel.query.get(s.personnel_id)
        if p:
            result.append({**s.to_dict(), "rank": p.rank, "unit_name": p.unit_name,
                           "name": p.name, "deployment_zone": p.deployment_zone})
    return jsonify(result), 200
