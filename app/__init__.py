from flask import Flask, jsonify

from app.config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    return app
