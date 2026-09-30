from flask import Flask
from .config import config
from .extensions import db, jwt, bcrypt, cors, mail, migrate, limiter
from .middleware.error_handlers import register_error_handlers
from .jobs.scheduler import init_scheduler

def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False
    }})
    mail.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Start background scheduler
    with app.app_context():
        init_scheduler(app)

    # Root UI dashboard
    @app.route("/")
    def index():
        from flask import render_template
        return render_template("index.html")

    return app

