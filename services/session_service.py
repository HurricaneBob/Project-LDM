"""Orchestrates play sessions across APIs."""
import json

from config import Config
from models.extensions import db
from models.play_session import PlaySession
from models.relationship import Relationship
from models.session_agent import SessionAgent
from models.turn import Turn
from services.cpb_adapter import (
    build_from_profile,
    dict_to_profile,
    snapshot_to_dict,
)
from services.memory_service import MemoryService
from services.relationship_graph import Edge, RelationshipGraph
from services.scenario_manager import ScenarioManager
from services.state_engine import StateEngine
from services.stabilization import is_stabilized
from llm.llm_service import LLMService


def _default_internal():
    return {
        "emotion": "tense",
        "confidence": 45,
        "stress": 60,
        "fatigue": 35,
    }


class SessionService:
    @staticmethod
    def _load_session(session_id: str) -> PlaySession:
        session = db.session.get(PlaySession, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return session

    @staticmethod
    def _build_agents_public(session: PlaySession) -> list[dict]:
        result = []
        for sa in session.session_agents:
            result.append(
                {
                    "id": sa.agent_id,
                    "name": sa.agent.name,
                    "role": sa.agent.role,
                    "static_params": sa.agent.static_params,
                    "internal_dynamic": sa.internal_dynamic,
                }
            )
        return result

    @staticmethod
    def _build_cpb_map(session: PlaySession) -> dict:
        cpb = {}
        for sa in session.session_agents:
            profile = dict_to_profile(sa.cpb_snapshot) if sa.cpb_snapshot else sa.agent.cpb_profile
            cpb[sa.agent_id] = build_from_profile(profile)
        return cpb

    @staticmethod
    def _agents_state_map(session: PlaySession) -> dict:
        return {
            sa.agent_id: {
                "static_params": sa.agent.static_params,
                "internal_dynamic": sa.internal_dynamic,
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
            if row:
                row.trust = e["trust"]
                row.respect = e["respect"]
                row.relationship = e["relationship"]
                row.communication_quality = e.get("communication_quality", e["relationship"])
            else:
                db.session.add(
                    Relationship(
                        session_id=session_id,
                        from_id=e["from_id"],
                        to_id=e["to_id"],
                        trust=e["trust"],
                        respect=e["respect"],
                        relationship=e["relationship"],
                        communication_quality=e.get("communication_quality", e["relationship"]),
                    )
                )

    @staticmethod
    def get_state_summary(session_id: str) -> dict:
        session = SessionService._load_session(session_id)
        scenario = ScenarioManager.get_by_id(session.current_scenario_id)
        graph = SessionService._load_graph(session)
        from services.cohesion import calculate_cohesion

        cohesion = calculate_cohesion(graph, scenario.delta_weights if scenario else None)
        agents = SessionService._build_agents_public(session)
        edges = graph.to_list()

        p = session.turns[-1].p_stabilize if session.turns else 0.0

        return {
            "session_id": session.id,
            "status": session.status,
            "current_scenario_index": session.current_scenario_index,
            "scenario": scenario.to_dict() if scenario else None,
            "agents": agents,
            "relationships": edges,
            "cohesion": cohesion,
            "p_stabilize": p,
            "turn_count": session.turn_count,
        }

    @staticmethod
    def init_scenario(
        session_id: str | None = None,
        scenario_id: str | None = None,
        scenario_index: int | None = None,
    ) -> dict:
        if scenario_id:
            scenario = ScenarioManager.get_by_id(scenario_id)
        elif scenario_index:
            scenario = ScenarioManager.get_by_index(scenario_index)
        else:
            scenario = ScenarioManager.get_by_index(1)

        if not scenario:
            raise ValueError("Scenario not found")

        agents = ScenarioManager.get_agents_for_scenario(scenario.id)
        if not agents:
            raise ValueError("Scenario has no agents")

        if session_id:
            session = SessionService._load_session(session_id)
            session.current_scenario_id = scenario.id
            session.current_scenario_index = scenario.sequence_index
            session.turn_count = 0
            SessionAgent.query.filter_by(session_id=session.id).delete()
            Relationship.query.filter_by(session_id=session.id).delete()
        else:
            session = PlaySession(
                current_scenario_id=scenario.id,
                current_scenario_index=scenario.sequence_index,
            )
            db.session.add(session)
            db.session.flush()

        cpb_map = {}
        for agent in agents:
            pb = build_from_profile(agent.cpb_profile)
            cpb_map[agent.id] = pb
            snapshot = snapshot_to_dict(pb)
            sa = SessionAgent(
                session_id=session.id,
                agent_id=agent.id,
                internal_dynamic=_default_internal(),
                cpb_snapshot=snapshot,
            )
            db.session.add(sa)

        graph = RelationshipGraph()
        for agent in agents:
            graph.ensure_edge(
                RelationshipGraph.LEADER_ID,
                agent.id,
                {"trust": 48, "respect": 50, "relationship": 47},
            )
            graph.ensure_edge(
                agent.id,
                RelationshipGraph.LEADER_ID,
                {"trust": 45, "respect": 48, "relationship": 45},
            )
        SessionService._persist_graph(session.id, graph)

        agents_public = [
            {"id": a.id, "name": a.name, "role": a.role} for a in agents
        ]

        if scenario.cached_opening_narration:
            opening_data = json.loads(scenario.cached_opening_narration)
            opening_narration = opening_data.get("opening_narration", "")
            lines = opening_data.get("lines", [])
        else:
            opening = LLMService.generate_opening(
                scenario.opening_situation, agents_public
            )
            opening_narration = opening.opening_narration
            lines = [
                ln.model_dump() if hasattr(ln, "model_dump") else ln
                for ln in opening.lines
            ]
            scenario.cached_opening_narration = json.dumps(
                {"opening_narration": opening_narration, "lines": lines}
            )

        session.last_dialogue = lines
        db.session.commit()

        state = SessionService.get_state_summary(session.id)
        return {
            "session_id": session.id,
            "scenario": scenario.to_dict(),
            "agents_public": SessionService._build_agents_public(session),
            "opening_narration": opening_narration,
            "dialogue": lines,
            "state_summary": state,
        }

    @staticmethod
    def interact(session_id: str, user_message: str) -> dict:
        session = SessionService._load_session(session_id)
        scenario = ScenarioManager.get_by_id(session.current_scenario_id)
        if not scenario:
            raise ValueError("No active scenario")

        if session.turn_count >= Config.MAX_TURNS_PER_SCENARIO:
            raise ValueError("Maximum turns reached for this scenario")

        agents_public = [
            {"id": sa.agent_id, "name": sa.agent.name, "role": sa.agent.role}
            for sa in session.session_agents
        ]

        classification = LLMService.classify_communication(
            scenario.opening_situation, agents_public, user_message
        )

        targets = classification.targets or [a["id"] for a in agents_public]
        cpb_map = SessionService._build_cpb_map(session)
        agents_state = SessionService._agents_state_map(session)
        graph = SessionService._load_graph(session)

        applied = StateEngine.apply_communication(
            classification.tone,
            targets,
            agents_state,
            graph,
            cpb_map,
            scenario.delta_weights,
        )

        for sa in session.session_agents:
            if sa.agent_id in agents_state:
                sa.internal_dynamic = agents_state[sa.agent_id]["internal_dynamic"]
                if sa.agent_id in cpb_map:
                    sa.cpb_snapshot = snapshot_to_dict(cpb_map[sa.agent_id])

        SessionService._persist_graph(session.id, graph)

        if MemoryService.should_extract(classification.tone, applied):
            mem_text = LLMService.extract_memory(
                classification.tone,
                user_message,
                json.dumps(applied.get("per_agent", {}))[:500],
            )
            MemoryService.add(session.id, mem_text)

        memories = MemoryService.get_recent(session.id)
        state_snapshot = json.dumps(SessionService.get_state_summary(session.id), indent=0)[
            :2000
        ]
        last_dialogue = json.dumps(session.last_dialogue or [])[:800]

        dialogue = LLMService.generate_dialogue(
            scenario.opening_situation,
            state_snapshot,
            memories,
            last_dialogue,
            user_message,
            classification.tone,
        )

        lines = [
            ln.model_dump() if hasattr(ln, "model_dump") else ln
            for ln in dialogue.lines
        ]
        session.last_dialogue = lines
        session.turn_count += 1

        turn = Turn(
            session_id=session.id,
            scenario_id=scenario.id,
            turn_index=session.turn_count,
            user_text=user_message,
            llm_summary=dialogue.turn_summary,
            applied_delta=applied,
            cohesion=applied.get("cohesion"),
            p_stabilize=applied.get("p_stabilize"),
        )
        db.session.add(turn)

        p_stab = applied.get("p_stabilize", 0)
        cohesion = applied.get("cohesion", 50)
        scenario_complete = is_stabilized(p_stab, scenario.stabilization_threshold)
        next_scenario_id = None

        if scenario_complete:
            ScenarioManager.complete_scenario(
                session.id,
                scenario,
                session.turn_count,
                cohesion,
                p_stab,
                {"applied": applied},
            )
            next_sc = ScenarioManager.next_scenario(scenario.sequence_index)
            if next_sc:
                session.current_scenario_index = next_sc.sequence_index
                db.session.commit()
                init_result = SessionService.init_scenario(
                    session_id=session.id, scenario_id=next_sc.id
                )
                next_scenario_id = next_sc.id
                return {
                    "dialogue": lines,
                    "narration": dialogue.narration,
                    "state_summary": init_result["state_summary"],
                    "cohesion": cohesion,
                    "p_stabilize": p_stab,
                    "scenario_complete": True,
                    "next_scenario_id": next_scenario_id,
                    "opening_narration": init_result.get("opening_narration"),
                    "turn_summary": dialogue.turn_summary,
                }
            session.status = "completed"
        db.session.commit()

        return {
            "dialogue": lines,
            "narration": dialogue.narration,
            "state_summary": SessionService.get_state_summary(session.id),
            "cohesion": cohesion,
            "p_stabilize": p_stab,
            "scenario_complete": scenario_complete,
            "next_scenario_id": next_scenario_id,
            "turn_summary": dialogue.turn_summary,
        }

    @staticmethod
    def final_evaluation(session_id: str) -> dict:
        session = SessionService._load_session(session_id)
        summaries = session.summaries
        summary_text = "\n".join(
            f"- {s.summary_text}" for s in summaries
        ) or "No completed scenarios yet."

        turns = Turn.query.filter_by(session_id=session.id).order_by(Turn.turn_index).all()
        trust_trend = [t.applied_delta.get("mean_trust") for t in turns if t.applied_delta]
        trends = f"Trust trend: {trust_trend}\nTurns: {len(turns)}"

        memories = MemoryService.get_recent(session.id, limit=20)
        evaluation = LLMService.final_evaluation(summary_text, trends, memories)

        from llm.gemini_client import get_token_usage

        return {
            "session_id": session_id,
            "evaluation": evaluation.model_dump(),
            "token_usage": get_token_usage(),
        }
