def register_blueprints(app):
    from .auth import auth_bp
    from .personnel import personnel_bp
    from .risk import risk_bp
    from .wellness import wellness_bp
    from .alerts import alerts_bp
    from .dashboard import dashboard_bp
    from .reports import reports_bp
    from .admin import admin_bp
    from .rag import rag_bp

    app.register_blueprint(auth_bp,      url_prefix="/api/auth")
    app.register_blueprint(personnel_bp, url_prefix="/api/personnel")
    app.register_blueprint(risk_bp,      url_prefix="/api/risk")
    app.register_blueprint(wellness_bp,  url_prefix="/api/wellness")
    app.register_blueprint(alerts_bp,    url_prefix="/api/alerts")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(reports_bp,   url_prefix="/api/reports")
    app.register_blueprint(admin_bp,     url_prefix="/api/admin")
    app.register_blueprint(rag_bp,       url_prefix="/api/rag")
