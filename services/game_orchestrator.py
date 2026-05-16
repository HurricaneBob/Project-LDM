"""Game flow: llm_call_schemas call types + signal engine + /api/chat contract."""
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
        scenario = ScenarioManager.get_by_index(scenario_index)
        if not scenario:
            raise ValueError(f"Scenario {scenario_index} not found")

        persona_keys = active_agents_for_scenario(scenario_index)
        agents = []
        for key in persona_keys:
            agent = Agent.query.filter_by(slug=key).first()
            if agent:
                agents.append(agent)

        session.current_scenario_id = scenario.id
        session.current_scenario_index = scenario_index
        session.turn_count = 0
        SessionAgent.query.filter_by(session_id=session.id).delete()
        Relationship.query.filter_by(session_id=session.id).delete()

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
        for agent in agents:
            slug = _agent_slug(agent)
            graph.ensure_edge("leader", slug, {"trust": 48, "respect": 50, "relationship": 47})
            graph.ensure_edge(slug, "leader", {"trust": 45, "respect": 48, "relationship": 45})
        GameOrchestrator._persist_graph(session.id, graph)

        compressed = {"memory_summary": [], "environmental_state": session.environmental_state}
        if scenario_index == 1:
            init = LLMService.game_init(1, persona_keys)
            session.situation_brief = init.situation_brief
        else:
            init = LLMService.scenario_init(scenario_index, persona_keys, compressed)
            session.situation_brief = init.situation_brief

        if not session.situation_brief:
            session.situation_brief = scenario.opening_situation

        db.session.flush()
        return scenario, persona_keys

    @staticmethod
    def chat(session_id: str | None, message: str, history: list | None = None) -> dict:
        history = history or []
        is_new = not session_id

        if is_new:
            session = PlaySession(current_scenario_index=1)
            db.session.add(session)
            db.session.flush()
            GameOrchestrator._init_session_state(session)
            scenario, persona_keys = GameOrchestrator._setup_scenario(session, 1)
        else:
            session = GameOrchestrator._load(session_id)
            GameOrchestrator._init_session_state(session)
            scenario = ScenarioManager.get_by_id(session.current_scenario_id)
            persona_keys = GameOrchestrator._active_persona_ids(session)

        if session.turn_count >= Config.MAX_TURNS_PER_SCENARIO:
            raise ValueError("Maximum turns reached for this scenario")

        agents_state = GameOrchestrator._agents_state(session)
        graph = GameOrchestrator._load_graph(session)

        context = session.situation_brief or (scenario.opening_situation if scenario else "")
        analysis = LLMService.semantic_analysis(message, persona_keys, context[:300])
        signals = analysis.communication_signals.model_dump()
        style = analysis.leadership_style_tag

        counts = session.leadership_style_counts or {}
        counts[style] = counts.get(style, 0) + 1
        session.leadership_style_counts = counts

        applied = SignalEngine.apply_signals(
            signals,
            style,
            persona_keys,
            agents_state,
            graph,
            session.user_psych,
            session.environmental_state,
            session.hidden_variables,
            scenario.delta_weights if scenario else None,
        )

        for sa in session.session_agents:
            slug = _agent_slug(sa.agent)
            if slug in agents_state:
                sa.internal_dynamic = agents_state[slug]["internal_dynamic"]

        GameOrchestrator._persist_graph(session.id, graph)

        if MemoryService.should_extract(style, applied):
            mem = LLMService.extract_memory(style, message, json.dumps(signals)[:400])
            MemoryService.add(session.id, mem)

        compressed = GameOrchestrator._compressed_state(session, graph)
        dialogue = LLMService.dialogue_generation(
            persona_keys, compressed, message, max_speakers=min(3, len(persona_keys))
        )

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
                GameOrchestrator._setup_scenario(session, next_sc.sequence_index)
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
