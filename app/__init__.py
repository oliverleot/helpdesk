from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)

    from app import models  # noqa: F401

    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return db.session.get(User, int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.tickets import tickets_bp
    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    return app
