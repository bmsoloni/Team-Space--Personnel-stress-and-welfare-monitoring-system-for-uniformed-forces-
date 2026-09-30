from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.wellness_assessment import WellnessAssessment
from ..middleware.rbac import medical_or_above
from sqlalchemy import desc

wellness_bp = Blueprint("wellness", __name__)

QUESTIONS = [
    {"id": 1, "text": "How would you rate your overall mood today?", "type": "scale", "min": 1, "max": 10},
    {"id": 2, "text": "How well did you sleep last night?", "type": "scale", "min": 1, "max": 10},
    {"id": 3, "text": "How is your energy level?", "type": "scale", "min": 1, "max": 10},
    {"id": 4, "text": "How stressed do you feel right now?", "type": "scale", "min": 1, "max": 10},
    {"id": 5, "text": "Do you feel supported by your colleagues and family?", "type": "scale", "min": 1, "max": 10},
    {"id": 6, "text": "Are you experiencing any physical discomfort or pain?", "type": "yesno"},
    {"id": 7, "text": "Do you feel motivated to perform your duties?", "type": "scale", "min": 1, "max": 10},
    {"id": 8, "text": "Have you had thoughts of harming yourself or others? (Confidential)", "type": "yesno"},
    {"id": 9, "text": "Would you like to speak with a welfare officer?", "type": "yesno"},
]

@wellness_bp.route("/questions", methods=["GET"])
@jwt_required()
def get_questions():
    return jsonify({"questions": QUESTIONS}), 200

@wellness_bp.route("/submit", methods=["POST"])
@jwt_required()
def submit():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data.get("consent_given"):
        return jsonify({"error": "Consent is required to submit wellness assessment"}), 400
    personnel_id = data.get("personnel_id")
    mood = data.get("mood_score", 5)
    sleep = data.get("sleep_quality", 5)
    energy = data.get("energy_level", 5)
    stress = data.get("stress_level", 5)
    social = data.get("social_support", 5)
    # Compute composite score (higher = better wellness)
    score = ((mood + sleep + energy + (10 - stress) + social) / 5) * 10
    assessment = WellnessAssessment(
        personnel_id=personnel_id, score=round(score, 2),
        mood_score=mood, sleep_quality=sleep, energy_level=energy,
        stress_level=stress, social_support=social,
        responses=data.get("responses", {}), consent_given=True,
    )
    db.session.add(assessment)
    db.session.commit()
    return jsonify({"message": "Assessment submitted", "score": score}), 201

@wellness_bp.route("/history/<int:id>", methods=["GET"])
@jwt_required()
@medical_or_above
def history(id):
    records = WellnessAssessment.query.filter_by(personnel_id=id).order_by(desc(WellnessAssessment.submitted_at)).limit(20).all()
    return jsonify([r.to_dict() for r in records]), 200

@wellness_bp.route("/summary", methods=["GET"])
@jwt_required()
@medical_or_above
def summary():
    from sqlalchemy import func
    avg = db.session.query(func.avg(WellnessAssessment.score)).scalar()
    count = WellnessAssessment.query.count()
    return jsonify({"avg_wellness_score": round(float(avg or 0), 2), "total_submissions": count}), 200
