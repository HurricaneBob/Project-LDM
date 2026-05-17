"""Flask app with inline Gemini generate_content for interactive chat."""
import json
import logging
import os
from typing import Type, TypeVar

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from pydantic import BaseModel

load_dotenv()

from config import Config
from models.extensions import db, migrate

logger = logging.getLogger("ldm.app")
T = TypeVar("T", bound=BaseModel)


def _gemini_client():
    from google import genai

    return genai.Client(api_key=Config.GEMINI_API_KEY)


def call_gemini_json(
    purpose: str,
    prompt: str,
    schema: Type[T],
    model: str | None = None,
) -> T:
    """Call Gemini generate_content and parse JSON into a Pydantic model."""
    from llm.gemini_client import (
        GeminiAPIError,
        _log_call,
        _mock_response,
        get_token_usage,
    )

    _log_call(purpose, len(prompt))

    if Config.LLM_MOCK or not Config.GEMINI_API_KEY:
        if not Config.LLM_MOCK and not Config.GEMINI_API_KEY:
            logger.warning("No GEMINI_API_KEY; using mock for %s", purpose)
        data = _mock_response(purpose)
        return schema.model_validate(data)

    client = _gemini_client()
    model_name = model or Config.GEMINI_MODEL_FLASH

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
    except Exception as e:
        raise GeminiAPIError(purpose, model_name, str(e)) from e

    text = response.text or "{}"
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        cleaned = text.strip().removeprefix("```json").removesuffix("```").strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise GeminiAPIError(
                purpose, model_name, f"invalid JSON in response: {text[:200]}"
            ) from e

    try:
        return schema.model_validate(data)
    except Exception as e:
        raise GeminiAPIError(purpose, model_name, f"schema validation failed: {e}") from e


def get_llm_mode() -> str:
    if Config.LLM_MOCK:
        return "mock"
    if not Config.GEMINI_API_KEY:
        return "mock"
    return "live"


def log_llm_startup():
    mode = get_llm_mode()
    if Config.LLM_MOCK:
        logger.warning("LLM mode: mock (LLM_MOCK=1)")
    elif not Config.GEMINI_API_KEY:
        logger.warning("LLM mode: mock (GEMINI_API_KEY not set)")
    else:
        logger.info(
            "LLM mode: live (model=%s, eval=%s)",
            Config.GEMINI_MODEL_FLASH,
            Config.GEMINI_MODEL_EVAL,
        )
    return mode


def handle_chat_turn(
    session_id: str | None,
    message: str,
    history: list | None = None,
) -> dict:
    """Process one chat turn: seed JSON context + generate_content + SignalEngine."""
    from llm.schemas import (
        DialogueGenerationResponse,
        DialogueLine,
        GameInitResponse,
        ScenarioInitResponse,
        SemanticAnalysisResponse,
    )
    from models.play_session import PlaySession
    from models.turn import Turn
    from services.game_orchestrator import GameOrchestrator
    from services.json_context import (
        build_prompt,
        display_names_for_keys,
        get_scenario,
    )
    from services.memory_service import MemoryService
    from services.parameter_delta_mapper import signals_to_parameter_deltas
    from services.persona_map import to_display_name, to_persona_id
    from services.scenario_manager import ScenarioManager
    from services.signal_engine import SignalEngine
    from services.stabilization import is_stabilized

    history = history or []
    is_new = not session_id

    if is_new:
        session = PlaySession(current_scenario_index=1)
        db.session.add(session)
        db.session.flush()
        GameOrchestrator._init_session_state(session)
        scenario, persona_keys = _setup_scenario_with_gemini(session, 1)
    else:
        session = GameOrchestrator._load(session_id)
        GameOrchestrator._init_session_state(session)
        scenario = ScenarioManager.get_by_id(session.current_scenario_id)
        persona_keys = GameOrchestrator._active_persona_ids(session)

    if session.turn_count >= Config.MAX_TURNS_PER_SCENARIO:
        raise ValueError("Maximum turns reached for this scenario")

    scenario_index = session.current_scenario_index or 1
    seed_scenario = get_scenario(scenario_index)
    context = session.situation_brief or (
        seed_scenario.get("opening_situation") if seed_scenario else ""
    ) or (scenario.opening_situation if scenario else "")

    analysis_payload = {
        "user_input": message,
        "active_agents": display_names_for_keys(persona_keys),
        "scenario_context_summary": context[:300],
    }
    analysis_prompt = build_prompt(
        "3A_semantic_analysis", analysis_payload, scenario_index
    )
    analysis = call_gemini_json(
        "3A_semantic_analysis",
        analysis_prompt,
        SemanticAnalysisResponse,
    )
    signals = analysis.communication_signals.model_dump()
    style = analysis.leadership_style_tag

    counts = session.leadership_style_counts or {}
    counts[style] = counts.get(style, 0) + 1
    session.leadership_style_counts = counts

    agents_state = GameOrchestrator._agents_state(session)
    graph = GameOrchestrator._load_graph(session)

    delta_weights = None
    if seed_scenario:
        delta_weights = seed_scenario.get("delta_weights")
    elif scenario:
        delta_weights = scenario.delta_weights

    applied = SignalEngine.apply_signals(
        signals,
        style,
        persona_keys,
        agents_state,
        graph,
        session.user_psych,
        session.environmental_state,
        session.hidden_variables,
        delta_weights,
    )

    from services.game_orchestrator import _agent_slug

    for sa in session.session_agents:
        slug = _agent_slug(sa.agent)
        if slug in agents_state:
            sa.internal_dynamic = agents_state[slug]["internal_dynamic"]

    GameOrchestrator._persist_graph(session.id, graph)

    if MemoryService.should_extract(style, applied):
        mem_payload = {
            "tone": style,
            "user_message": message,
            "applied_delta": json.dumps(signals)[:400],
        }
        mem_prompt = build_prompt("memory", mem_payload, scenario_index)
        from llm.schemas import MemoryExtract

        mem_result = call_gemini_json("memory", mem_prompt, MemoryExtract)
        MemoryService.add(session.id, mem_result.memory)

    compressed = GameOrchestrator._compressed_state(session, graph)
    last_lines = session.last_dialogue or []
    last_dialogue = "\n".join(
        f"{r.get('personaId', 'agent')}: {r.get('message', '')}" for r in last_lines
    )

    dialogue_payload = {
        "active_agents": display_names_for_keys(persona_keys),
        "compressed_state": compressed,
        "user_message": message,
        "max_speakers": min(3, len(persona_keys)),
        "scenario_context_summary": context[:300],
        "tone": style,
        "last_dialogue": last_dialogue,
    }
    dialogue_prompt = build_prompt(
        "3B_dialogue_generation", dialogue_payload, scenario_index
    )
    dialogue_prompt += (
        f"\nReturn JSON with 'lines' array of up to {min(3, len(persona_keys))} "
        "objects: speaking_agent, ai_response. Optional narration string."
    )
    dialogue = call_gemini_json(
        "3B_dialogue_generation",
        dialogue_prompt,
        DialogueGenerationResponse,
    )
    if not dialogue.lines:
        dialogue.lines = [
            DialogueLine(
                speaking_agent=to_display_name(persona_keys[0]),
                ai_response="We need your direction on this before we can move forward.",
            )
        ]

    persona_responses = []
    for line in dialogue.lines:
        pid = to_persona_id(line.speaking_agent)
        persona_responses.append({"personaId": pid, "message": line.ai_response})

    if not persona_responses and is_new:
        persona_responses.append(
            {
                "personaId": persona_keys[0],
                "message": session.situation_brief or "The team awaits your leadership.",
            }
        )

    session.turn_count += 1
    session.last_dialogue = persona_responses

    turn = Turn(
        session_id=session.id,
        scenario_id=scenario.id if scenario else session.current_scenario_id,
        turn_index=session.turn_count,
        user_text=message,
        llm_summary=dialogue.narration or style,
        applied_delta=applied,
        cohesion=applied.get("cohesion"),
        p_stabilize=applied.get("p_stabilize"),
    )
    db.session.add(turn)

    param_deltas = signals_to_parameter_deltas(signals, style)
    p_stab = applied.get("p_stabilize", 0)
    cohesion = applied.get("cohesion", 50)
    session_title = None
    if is_new or session.turn_count == 1:
        words = message.strip().split()[:8]
        session_title = " ".join(words) + ("…" if len(message.split()) > 8 else "")
        session_title = session_title[:1].upper() + session_title[1:]

    scenario_complete = False
    if scenario and is_stabilized(p_stab, scenario.stabilization_threshold):
        scenario_complete = True
        ScenarioManager.complete_scenario(
            session.id,
            scenario,
            session.turn_count,
            cohesion,
            p_stab,
            {"signals": signals, "user_psych": session.user_psych},
        )
        next_sc = ScenarioManager.next_scenario(scenario.sequence_index)
        if next_sc:
            _setup_scenario_with_gemini(session, next_sc.sequence_index)
        else:
            session.status = "completed"

    db.session.commit()

    out = {
        "sessionId": session.id,
        "personaResponses": persona_responses,
        "parameterDeltas": param_deltas,
        "meta": {
            "cohesion": cohesion,
            "p_stabilize": p_stab,
            "scenario_index": session.current_scenario_index,
            "scenario_complete": scenario_complete,
        },
    }
    if session_title:
        out["sessionTitle"] = session_title
    if is_new and session.situation_brief:
        out["situationBrief"] = session.situation_brief
    return out


def _setup_scenario_with_gemini(session, scenario_index: int):
    """DB scenario setup + game/scenario init via generate_content."""
    from llm.schemas import GameInitResponse, ScenarioInitResponse
    from services.game_orchestrator import GameOrchestrator
    from services.json_context import build_prompt, display_names_for_keys, get_scenario
    from services.scenario_manager import ScenarioManager
    from services.schema_loader import active_agents_for_scenario

    scenario = ScenarioManager.get_by_index(scenario_index)
    if not scenario:
        raise ValueError(f"Scenario {scenario_index} not found")

    persona_keys = active_agents_for_scenario(scenario_index)
    seed = get_scenario(scenario_index)

    session.current_scenario_id = scenario.id
    session.current_scenario_index = scenario_index
    session.turn_count = 0

    from models.agent import Agent
    from models.relationship import Relationship
    from models.session_agent import SessionAgent
    from services.cpb_adapter import build_from_profile, snapshot_to_dict
    from services.relationship_graph import RelationshipGraph

    agents = []
    for key in persona_keys:
        agent = Agent.query.filter_by(slug=key).first()
        if agent:
            agents.append(agent)

    SessionAgent.query.filter_by(session_id=session.id).delete()
    Relationship.query.filter_by(session_id=session.id).delete()

    def _default_internal():
        return {"emotion": "tense", "confidence": 45, "stress": 60, "fatigue": 35}

    for agent in agents:
        pb = build_from_profile(agent.cpb_profile)
        db.session.add(
            SessionAgent(
                session_id=session.id,
                agent_id=agent.id,
                internal_dynamic=_default_internal(),
                cpb_snapshot=snapshot_to_dict(pb),
            )
        )

    graph = RelationshipGraph()
    from services.game_orchestrator import _agent_slug

    for agent in agents:
        slug = _agent_slug(agent)
        graph.ensure_edge("leader", slug, {"trust": 48, "respect": 50, "relationship": 47})
        graph.ensure_edge(slug, "leader", {"trust": 45, "respect": 48, "relationship": 45})
    GameOrchestrator._persist_graph(session.id, graph)

    compressed = {"memory_summary": [], "environmental_state": session.environmental_state}
    names = display_names_for_keys(persona_keys)
    ctx = (seed or {}).get("opening_situation") or scenario.opening_situation

    if scenario_index == 1:
        payload = {
            "scenario_id": 1,
            "active_agents": names,
            "scenario_context_summary": ctx,
        }
        prompt = build_prompt("1_game_init", payload, scenario_index)
        init = call_gemini_json("1_game_init", prompt, GameInitResponse)
        session.situation_brief = init.situation_brief
    else:
        payload = {
            "scenario_id": scenario_index,
            "active_agents": names,
            "compressed_state": compressed,
            "scenario_context_summary": ctx,
        }
        prompt = build_prompt("2_scenario_init", payload, scenario_index)
        init = call_gemini_json("2_scenario_init", prompt, ScenarioInitResponse)
        session.situation_brief = init.situation_brief

    if not session.situation_brief:
        session.situation_brief = ctx

    db.session.flush()
    return scenario, persona_keys


def create_app(config_class=Config):
    app = Flask(__name__, static_folder="static")
    app.config.from_object(config_class)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)

    log_llm_startup()

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
        return jsonify({
            "status": "ok",
            "service": "ldm-leadership-sim",
            "llm": get_llm_mode(),
        })

    @app.route("/api/session/<session_id>/state")
    def session_state(session_id):
        from services.session_service import SessionService

        try:
            return jsonify(SessionService.get_state_summary(session_id))
        except ValueError as e:
            return jsonify({"error": str(e)}), 404

    return app


if os.getenv("SKIP_APP_FACTORY"):
    app = None  # unit tests import call_gemini_json without full Flask stack
else:
    app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
