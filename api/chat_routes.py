from flask import Blueprint, jsonify, request

from services.game_orchestrator import GameOrchestrator

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    session_id = data.get("sessionId") or data.get("session_id")
    message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not message:
        return jsonify({"error": "message required"}), 400

    try:
        result = GameOrchestrator.chat(session_id, message, history)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
