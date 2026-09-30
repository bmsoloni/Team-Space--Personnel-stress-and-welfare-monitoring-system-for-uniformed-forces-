from flask import Blueprint, request, jsonify
from flask_jwt_extended import (create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt)
from ..extensions import db, bcrypt
from ..models.user import User
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400
    user = User.query.filter_by(email=data["email"], is_active=True).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401
    user.last_login = datetime.utcnow()
    db.session.commit()
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }), 200

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    access_token = create_access_token(identity=str(user_id), additional_claims={"role": user.role})
    return jsonify({"access_token": access_token}), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully"}), 200

@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    data = request.get_json()
    if not bcrypt.check_password_hash(user.password_hash, data.get("current_password", "")):
        return jsonify({"error": "Current password is incorrect"}), 400
    user.password_hash = bcrypt.generate_password_hash(data["new_password"]).decode("utf-8")
    db.session.commit()
    return jsonify({"message": "Password updated successfully"}), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password") or not data.get("full_name"):
        return jsonify({"error": "Full name, email, and password required"}), 400
    
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "An officer account with this email already exists"}), 409
    
    pw_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user = User(
        email=data["email"],
        password_hash=pw_hash,
        full_name=data["full_name"],
        role=data.get("role", "welfare_officer"),
        unit_id=data.get("unit_id", 1)
    )
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({
        "message": "Officer account registered successfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }), 201
