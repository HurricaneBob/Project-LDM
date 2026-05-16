"""Deterministic parameter updates from classified communication."""
from typing import Any

from config import Config
from services.cpb_adapter import apply_leadership_event, get_modifiers
from services.cohesion import calculate_cohesion
from services.relationship_graph import RelationshipGraph
from services.stabilization import calculate_p_stabilize

TONE_DELTAS = {
    "supportive": {"trust": 4, "respect": 2, "relationship": 3, "stress": -3, "confidence": 3},
    "encouraging": {"trust": 3, "respect": 2, "relationship": 2, "stress": -2, "confidence": 2},
    "validating": {"trust": 3, "respect": 1, "relationship": 2, "stress": -2, "confidence": 2},
    "neutral": {"trust": 0, "respect": 0, "relationship": 0, "stress": 0, "confidence": 0},
    "neutral_cold": {"trust": -1, "respect": 0, "relationship": -1, "stress": 1, "confidence": -1},
    "dismissive": {"trust": -3, "respect": -2, "relationship": -4, "stress": 4, "confidence": -3},
    "blaming": {"trust": -5, "respect": -3, "relationship": -6, "stress": 5, "confidence": -4},
    "aggressive": {"trust": -6, "respect": -4, "relationship": -7, "stress": 6, "confidence": -5},
}


def clamp(value: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, value))


def apply_momentum(old: float, delta: float, baseline: float = 50.0) -> float:
    momentum = Config.EMOTIONAL_MOMENTUM
    return clamp(old + delta + momentum * (old - baseline) * 0.1)


class StateEngine:
    @staticmethod
    def apply_communication(
        tone: str,
        targets: list[str],
        agents_state: dict[str, dict],
        graph: RelationshipGraph,
        cpb_instances: dict[str, Any],
        scenario_weights: dict | None = None,
    ) -> dict:
        """
        agents_state: agent_id -> {internal_dynamic, static_params}
        Returns applied_delta summary.
        """
        tone = tone.lower() if tone else "neutral"
        base = TONE_DELTAS.get(tone, TONE_DELTAS["neutral"])
        weights = scenario_weights or {}
        applied = {"tone": tone, "per_agent": {}, "edges": []}

        target_ids = targets if targets else list(agents_state.keys())

        for agent_id in target_ids:
            if agent_id not in agents_state:
                continue
            state = agents_state[agent_id]
            static = state.get("static_params", {})
            internal = state["internal_dynamic"]
            pb = cpb_instances.get(agent_id)
            mods = get_modifiers(pb) if pb else static

            patience_factor = (static.get("patience", 50) + mods.get("patience", 50)) / 100
            resilience = (static.get("resilience", 50) + mods.get("resilience", 50)) / 100
            rejection = mods.get("rejection_sensitivity", 50) / 100

            trust_d = base["trust"] * weights.get("trust", 1.0)
            respect_d = base["respect"] * weights.get("respect", 1.0)
            rel_d = base["relationship"] * weights.get("relationship", 1.0)
            stress_d = base["stress"] * weights.get("stress", 1.0)

            if tone in ("blaming", "aggressive", "dismissive"):
                trust_d *= 1 + rejection * 0.3
                rel_d *= 1 + rejection * 0.2
            if tone in ("supportive", "encouraging", "validating"):
                trust_d *= patience_factor
                stress_d *= resilience

            graph.apply_delta(
                RelationshipGraph.LEADER_ID,
                agent_id,
                trust=trust_d,
                respect=respect_d,
                relationship=rel_d,
            )
            graph.apply_delta(
                agent_id,
                RelationshipGraph.LEADER_ID,
                trust=trust_d * 0.6,
                respect=respect_d * 0.5,
                relationship=rel_d * 0.5,
            )

            internal["stress"] = apply_momentum(internal.get("stress", 50), stress_d)
            internal["confidence"] = apply_momentum(
                internal.get("confidence", 50), base["confidence"]
            )
            internal["fatigue"] = apply_momentum(
                internal.get("fatigue", 30), 0.5 if tone in ("blaming", "aggressive") else 0
            )
            if tone in ("supportive", "encouraging"):
                internal["emotion"] = "calm"
            elif tone in ("blaming", "aggressive"):
                internal["emotion"] = "tense"
            else:
                internal["emotion"] = internal.get("emotion", "neutral")

            if pb:
                apply_leadership_event(pb, tone, magnitude=1.0 + rejection * 0.2)

            applied["per_agent"][agent_id] = {
                "trust_delta": trust_d,
                "stress_delta": stress_d,
                "internal": dict(internal),
            }
            applied["edges"].append(
                {"from": "leader", "to": agent_id, "trust_delta": trust_d}
            )

        cohesion = calculate_cohesion(graph, scenario_weights)
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
