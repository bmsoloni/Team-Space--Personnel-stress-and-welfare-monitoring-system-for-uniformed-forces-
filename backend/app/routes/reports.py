from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..middleware.rbac import welfare_or_admin
from ..services.report_service import generate_pdf_report, generate_excel_report
import os, io

reports_bp = Blueprint("reports", __name__)
_reports_cache = {}

@reports_bp.route("/generate", methods=["POST"])
@jwt_required()
@welfare_or_admin
def generate():
    data = request.get_json() or {}
    fmt = data.get("format", "pdf")
    report_type = data.get("type", "unit_summary")
    user_id = get_jwt_identity()
    if fmt == "pdf":
        buf, filename = generate_pdf_report(report_type, data)
    else:
        buf, filename = generate_excel_report(report_type, data)
    report_id = f"{user_id}_{filename}"
    _reports_cache[report_id] = (buf, filename, fmt)
    return jsonify({"report_id": report_id, "filename": filename, "format": fmt}), 200

@reports_bp.route("/", methods=["GET"])
@jwt_required()
@welfare_or_admin
def list_reports():
    user_id = get_jwt_identity()
    user_reports = [{"id": k, "filename": v[1]} for k, v in _reports_cache.items() if k.startswith(str(user_id))]
    return jsonify(user_reports), 200

@reports_bp.route("/<path:report_id>/download", methods=["GET"])
@jwt_required()
@welfare_or_admin
def download(report_id):
    if report_id not in _reports_cache:
        return jsonify({"error": "Report not found"}), 404
    buf, filename, fmt = _reports_cache[report_id]
    buf.seek(0)
    mime = "application/pdf" if fmt == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return send_file(buf, mimetype=mime, as_attachment=True, download_name=filename)
