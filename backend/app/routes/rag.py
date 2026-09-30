from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..middleware.rbac import welfare_or_admin, commander_or_above
from ..middleware.audit import audit_log
from ..models.rag_conversation import RagConversation
from ..rag.rag_chain import run_rag_query
from ..rag.use_cases.welfare_recommender import get_welfare_recommendation
from ..rag.use_cases.case_similarity import find_similar_cases
from ..rag.use_cases.shap_explainer_rag import explain_risk_in_natural_language
from ..extensions import db
import uuid

rag_bp = Blueprint("rag", __name__)

@rag_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    user_id = get_jwt_identity()
    data = request.get_json()
    question = data.get("question", "")
    session_id = data.get("session_id", str(uuid.uuid4()))
    if not question:
        return jsonify({"error": "Question is required"}), 400
    result = run_rag_query(question, use_case="CHATBOT")
    conv = RagConversation(
        user_id=user_id, session_id=session_id, use_case="CHATBOT",
        question=question, answer=result["answer"],
        source_docs=result.get("sources"), model_used=result.get("model_used"),
    )
    db.session.add(conv)
    db.session.commit()
    return jsonify(result), 200

@rag_bp.route("/recommend/<int:personnel_id>", methods=["POST"])
@jwt_required()
@welfare_or_admin
@audit_log("RAG_RECOMMEND", "personnel")
def recommend(personnel_id):
    user_id = get_jwt_identity()
    result = get_welfare_recommendation(personnel_id)
    conv = RagConversation(
        user_id=user_id, session_id=str(uuid.uuid4()), use_case="RECOMMENDATION",
        question=f"Welfare recommendation for personnel {personnel_id}",
        answer=result["answer"], source_docs=result.get("sources"),
        model_used=result.get("model_used"),
    )
    db.session.add(conv)
    db.session.commit()
    return jsonify(result), 200

@rag_bp.route("/similar-cases/<int:personnel_id>", methods=["GET"])
@jwt_required()
@welfare_or_admin
def similar_cases(personnel_id):
    result = find_similar_cases(personnel_id)
    return jsonify(result), 200

@rag_bp.route("/explain-score/<int:personnel_id>", methods=["POST"])
@jwt_required()
@welfare_or_admin
@audit_log("RAG_EXPLAIN", "risk_scores")
def explain_score(personnel_id):
    user_id = get_jwt_identity()
    result = explain_risk_in_natural_language(personnel_id)
    conv = RagConversation(
        user_id=user_id, session_id=str(uuid.uuid4()), use_case="EXPLANATION",
        question=f"Explain risk factors for personnel {personnel_id}",
        answer=result["answer"], source_docs=result.get("sources"),
        model_used=result.get("model_used"),
    )
    db.session.add(conv)
    db.session.commit()
    return jsonify(result), 200

@rag_bp.route("/companion", methods=["POST"])
@jwt_required()
def companion():
    user_id = get_jwt_identity()
    data = request.get_json()
    question = data.get("message", "")
    session_id = data.get("session_id", str(uuid.uuid4()))
    result = run_rag_query(question, use_case="COMPANION")
    conv = RagConversation(
        user_id=user_id, session_id=session_id, use_case="COMPANION",
        question=question, answer=result["answer"],
        source_docs=result.get("sources"), model_used=result.get("model_used"),
    )
    db.session.add(conv)
    db.session.commit()
    return jsonify(result), 200

@rag_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = get_jwt_identity()
    convs = RagConversation.query.filter_by(user_id=user_id).order_by(RagConversation.created_at.desc()).limit(50).all()
    return jsonify([c.to_dict() for c in convs]), 200
