from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app import models  # noqa: F401

    migrate.init_app(app, db)

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    return app
