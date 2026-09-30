from functools import wraps
from flask import request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..extensions import db
from ..models.audit_log import AuditLog

def audit_log(action, target_table=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
            except Exception:
                user_id = None
            result = fn(*args, **kwargs)
            try:
                log = AuditLog(
                    user_id=user_id, action=action,
                    target_table=target_table,
                    target_id=kwargs.get("id") or kwargs.get("personnel_id"),
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get("User-Agent", "")[:500],
                )
                db.session.add(log)
                db.session.commit()
            except Exception:
                pass
            return result
        return wrapper
    return decorator
