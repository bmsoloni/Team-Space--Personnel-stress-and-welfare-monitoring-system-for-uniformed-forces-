from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify
from ..models.user import User

def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id)) if user_id else None
            if not user or user.role not in roles:
                return jsonify({"error": "Access denied. Insufficient permissions."}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def welfare_or_admin(fn):
    return roles_required("welfare_officer", "super_admin")(fn)

def commander_or_above(fn):
    return roles_required("commander", "welfare_officer", "super_admin")(fn)

def admin_only(fn):
    return roles_required("super_admin")(fn)

def medical_or_above(fn):
    return roles_required("medical_officer", "welfare_officer", "super_admin")(fn)

