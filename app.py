import os

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from models.extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__, static_folder="static")
    app.config.from_object(config_class)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)

    from api.chat_routes import chat_bp
    from api.evaluation_routes import evaluation_bp
    from api.scenario_routes import scenario_bp

    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(scenario_bp, url_prefix="/api/scenario")
    app.register_blueprint(evaluation_bp, url_prefix="/api/evaluation")

    from pathlib import Path

    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    @app.route("/")
    def index():
        return app.send_static_file("test_client.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "ldm-leadership-sim"})

    @app.route("/api/session/<session_id>/state")
    def session_state(session_id):
        from services.session_service import SessionService

        try:
            return jsonify(SessionService.get_state_summary(session_id))
        except ValueError as e:
            return jsonify({"error": str(e)}), 404

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
