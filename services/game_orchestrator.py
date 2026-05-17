"""Game flow: delegates chat to app.handle_chat_turn (inline generate_content)."""
import json

from config import Config
from models.agent import Agent
from models.extensions import db
from models.play_session import PlaySession
from models.relationship import Relationship
from models.session_agent import SessionAgent
from models.turn import Turn
from services.cpb_adapter import build_from_profile, snapshot_to_dict
from services.memory_service import MemoryService
from services.parameter_delta_mapper import signals_to_parameter_deltas
from services.persona_map import to_persona_id
from services.relationship_graph import RelationshipGraph
from services.scenario_manager import ScenarioManager
from services.signal_engine import (
    SignalEngine,
    default_environmental,
    default_hidden,
    default_user_psych,
)
from services.stabilization import is_stabilized
from services.schema_loader import active_agents_for_scenario
from llm.llm_service import LLMService


def _default_internal():
    return {"emotion": "tense", "confidence": 45, "stress": 60, "fatigue": 35}


def _agent_slug(agent: Agent) -> str:
    return getattr(agent, "slug", None) or to_persona_id(agent.name)


class GameOrchestrator:
    @staticmethod
    def _load(session_id: str) -> PlaySession:
        session = db.session.get(PlaySession, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return session

    @staticmethod
    def _init_session_state(session: PlaySession):
        if not session.user_psych:
            session.user_psych = default_user_psych()
        if not session.environmental_state:
            session.environmental_state = default_environmental()
        if not session.hidden_variables:
            session.hidden_variables = default_hidden()
        if not session.leadership_style_counts:
            session.leadership_style_counts = {}

    @staticmethod
    def _active_persona_ids(session: PlaySession) -> list[str]:
        return [_agent_slug(sa.agent) for sa in session.session_agents]

    @staticmethod
    def _agents_state(session: PlaySession) -> dict:
        return {
            _agent_slug(sa.agent): {
                "agent_id": sa.agent_id,
                "static_params": sa.agent.static_params,
                "internal_dynamic": dict(sa.internal_dynamic or _default_internal()),
            }
            for sa in session.session_agents
        }

    @staticmethod
    def _load_graph(session: PlaySession) -> RelationshipGraph:
        return RelationshipGraph.from_db_rows(session.relationships)

    @staticmethod
    def _persist_graph(session_id: str, graph: RelationshipGraph):
        for e in graph.to_list():
            row = Relationship.query.filter_by(
                session_id=session_id, from_id=e["from_id"], to_id=e["to_id"]
            ).first()
            comm = e.get("communication_quality", e["relationship"])
            if row:
                row.trust = e["trust"]
                row.respect = e["respect"]
                row.relationship = e["relationship"]
                row.communication_quality = comm
            else:
                db.session.add(
                    Relationship(
                        session_id=session_id,
                        from_id=e["from_id"],
                        to_id=e["to_id"],
                        trust=e["trust"],
                        respect=e["respect"],
                        relationship=e["relationship"],
                        communication_quality=comm,
                    )
                )

    @staticmethod
    def _compressed_state(session: PlaySession, graph: RelationshipGraph) -> dict:
        mood = {}
        for sa in session.session_agents:
            internal = sa.internal_dynamic or {}
            stress = internal.get("stress", 50)
            conf = internal.get("confidence", 50)
            mood[_agent_slug(sa.agent)] = {
                "stress": "high" if stress > 65 else "moderate" if stress > 40 else "low",
                "confidence": "high" if conf > 65 else "moderate" if conf > 40 else "low",
            }
        rel = {}
        for e in graph.to_list():
            if e["from_id"] != "leader" and e["to_id"] == "leader":
                rel[f"{e['from_id']}_to_user"] = {
                    "trust": e["trust"],
                    "respect": e["respect"],
                    "communication_quality": e.get("communication_quality", e["relationship"]),
                }
        return {
            "memory_summary": MemoryService.get_recent(session.id, limit=5),
            "environmental_state": session.environmental_state or default_environmental(),
            "agent_mood_summary": mood,
            "relationship_summary": rel,
        }

    @staticmethod
    def _setup_scenario(session: PlaySession, scenario_index: int):
        from app import _setup_scenario_with_gemini

        return _setup_scenario_with_gemini(session, scenario_index)

    @staticmethod
    def chat(session_id: str | None, message: str, history: list | None = None) -> dict:
        from app import handle_chat_turn

        return handle_chat_turn(session_id, message, history)

    @staticmethod
    def final_evaluation(session_id: str) -> dict:
        session = GameOrchestrator._load(session_id)
        summaries = {f"scenario_{i+1}": s.summary_text or "" for i, s in enumerate(session.summaries)}
        if not summaries:
            summaries = {"scenario_1": session.situation_brief or "In progress"}

        psych = session.user_psych or default_user_psych()
        global_deltas = {k: f"50→{v:.0f}" for k, v in psych.items()}

        result = LLMService.holistic_summary(
            summaries,
            global_deltas,
            session.leadership_style_counts or {},
        )
        hr = result.holistic_results

        from llm.gemini_client import get_token_usage

        return {
            "session_id": session_id,
            "evaluation": {
                "leadership_analysis": hr.parameter_deltas_analysis,
                "strengths": [hr.leadership_pattern_summary],
                "weaknesses": [],
                "cohesion_impact": hr.leadership_pattern_summary,
                "emotional_impact": hr.hr_competency_verdict,
                "dimension_scores": {
                    "emotional_regulation": 7.0,
                    "conflict_mediation": 7.0,
                    "trust_building": 7.0,
                    "adaptability": 7.0,
                    "leadership_communication": 7.0,
                },
                "holistic_results": hr.model_dump(),
            },
            "token_usage": get_token_usage(),
        }
