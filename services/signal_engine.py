"""Deterministic updates from 3A communication signals (no LLM math)."""
from config import Config
from services.cohesion import calculate_cohesion
from services.relationship_graph import RelationshipGraph
from services.stabilization import calculate_p_stabilize


def clamp(value: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, value))


def default_user_psych() -> dict:
    return {
        "Character": 50.0,
        "Emotion": 50.0,
        "Environment": 50.0,
        "Motivation": 50.0,
        "Self_Esteem": 50.0,
    }


def default_environmental() -> dict:
    return {
        "deadline_pressure": 55.0,
        "workload": 50.0,
        "project_stability": 48.0,
    }


def default_hidden() -> dict:
    return {
        "volatility": 30.0,
        "burnout_risk": 20.0,
        "latent_resentment": 10.0,
        "emotional_sensitivity": 40.0,
    }


class SignalEngine:
    @staticmethod
    def apply_signals(
        signals: dict,
        leadership_style: str,
        active_agent_ids: list[str],
        agents_state: dict,
        graph: RelationshipGraph,
        user_psych: dict,
        environmental_state: dict,
        hidden_variables: dict,
        scenario_weights: dict | None = None,
    ) -> dict:
        empathy = float(signals.get("empathy", 0.5))
        clarity = float(signals.get("clarity", 0.5))
        decisiveness = float(signals.get("decisiveness", 0.5))
        aggression = float(signals.get("aggression", 0.2))
        supportiveness = float(signals.get("supportiveness", 0.5))
        adaptability = float(signals.get("adaptability", 0.5))

        weights = scenario_weights or {}
        trust_d = (empathy * 5 + clarity * 3) * weights.get("trust", 1.0)
        respect_d = (clarity * 4 - aggression * 5) * weights.get("respect", 1.0)
        comm_d = (supportiveness * 4 + adaptability * 2 - aggression * 3) * weights.get(
            "communication_quality", 1.0
        )
        stress_d = -(supportiveness * 4) * weights.get("stress", 1.0)
        confidence_d = (decisiveness * 3 - aggression * 2) * weights.get("confidence", 1.0)

        applied = {"per_agent": {}, "signals": signals, "leadership_style": leadership_style}

        for agent_id in active_agent_ids:
            if agent_id not in agents_state:
                continue
            internal = agents_state[agent_id]["internal_dynamic"]
            graph.apply_delta(
                RelationshipGraph.LEADER_ID,
                agent_id,
                trust=trust_d,
                respect=respect_d,
                relationship=comm_d,
            )
            graph.apply_delta(
                agent_id,
                RelationshipGraph.LEADER_ID,
                trust=trust_d * 0.6,
                respect=respect_d * 0.5,
                relationship=comm_d * 0.5,
            )
            internal["stress"] = clamp(internal.get("stress", 50) + stress_d)
            internal["confidence"] = clamp(internal.get("confidence", 50) + confidence_d)
            internal["fatigue"] = clamp(
                internal.get("fatigue", 30) + aggression * 2 - supportiveness
            )
            if supportiveness > 0.6:
                internal["emotion"] = "calm"
            elif aggression > 0.5:
                internal["emotion"] = "tense"
            applied["per_agent"][agent_id] = {
                "trust_delta": trust_d,
                "stress_delta": stress_d,
                "internal": dict(internal),
            }

        user_psych["Character"] = clamp(
            user_psych.get("Character", 50) + (empathy + adaptability) / 2 * 3 - aggression * 2
        )
        user_psych["Emotion"] = clamp(
            user_psych.get("Emotion", 50) + supportiveness * 3 - aggression * 4
        )
        user_psych["Motivation"] = clamp(
            user_psych.get("Motivation", 50) + supportiveness * 3 - aggression * 2
        )
        user_psych["Self_Esteem"] = clamp(
            user_psych.get("Self_Esteem", 50) + clarity * 2 - aggression * 2
        )

        environmental_state["deadline_pressure"] = clamp(
            environmental_state.get("deadline_pressure", 50) + decisiveness * 2 - supportiveness
        )
        environmental_state["workload"] = clamp(
            environmental_state.get("workload", 50) + aggression * 3 - adaptability
        )
        environmental_state["project_stability"] = clamp(
            environmental_state.get("project_stability", 50) + trust_d * 0.3 - aggression * 2
        )

        hidden_variables["volatility"] = clamp(
            hidden_variables.get("volatility", 30) + aggression * 8 - empathy * 4
        )
        hidden_variables["burnout_risk"] = clamp(
            hidden_variables.get("burnout_risk", 20) + aggression * 5 - supportiveness * 3
        )

        cohesion = calculate_cohesion(graph, weights)
        applied["cohesion"] = cohesion

        leader_edges = graph.leader_edges()
        if leader_edges:
            mt = sum(e.trust for e in leader_edges) / len(leader_edges)
            mr = sum(e.respect for e in leader_edges) / len(leader_edges)
            mrel = sum(e.relationship for e in leader_edges) / len(leader_edges)
        else:
            mt = mr = mrel = 50.0

        stresses = [a["internal_dynamic"]["stress"] for a in agents_state.values()]
        fatigues = [a["internal_dynamic"]["fatigue"] for a in agents_state.values()]
        ms = sum(stresses) / len(stresses) if stresses else 50
        mf = sum(fatigues) / len(fatigues) if fatigues else 30

        p_stab = calculate_p_stabilize(mt, mr, mrel, ms, mf, cohesion)
        applied["p_stabilize"] = p_stab
        applied["mean_trust"] = mt
        return applied
