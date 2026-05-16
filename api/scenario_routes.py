from flask import Blueprint, jsonify, request

from services.session_service import SessionService

scenario_bp = Blueprint("scenario", __name__)


@scenario_bp.route("/init", methods=["POST"])
def init_scenario():
    data = request.get_json(silent=True) or {}
    try:
        result = SessionService.init_scenario(
            session_id=data.get("session_id"),
            scenario_id=data.get("scenario_id"),
            scenario_index=data.get("scenario_index"),
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scenario_bp.route("/interact", methods=["POST"])
def interact():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    user_message = data.get("user_message", "").strip()

    if not session_id:
        return jsonify({"error": "session_id required"}), 400
    if not user_message:
        return jsonify({"error": "user_message required"}), 400

    try:
        result = SessionService.interact(session_id, user_message)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
