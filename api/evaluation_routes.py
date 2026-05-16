from flask import Blueprint, jsonify, request

from services.game_orchestrator import GameOrchestrator

evaluation_bp = Blueprint("evaluation", __name__)


@evaluation_bp.route("/final", methods=["POST"])
def final_evaluation():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    try:
        result = GameOrchestrator.final_evaluation(session_id)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
