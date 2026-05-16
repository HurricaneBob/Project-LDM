from services.relationship_graph import RelationshipGraph
from services.signal_engine import SignalEngine, default_hidden, default_user_psych


def test_signals_increase_trust():
    graph = RelationshipGraph()
    graph.ensure_edge("leader", "commander", {"trust": 50, "respect": 50, "relationship": 50})
    agents = {
        "commander": {
            "static_params": {"patience": 60},
            "internal_dynamic": {"stress": 60, "confidence": 50, "fatigue": 30},
        }
    }
    signals = {
        "empathy": 0.8,
        "clarity": 0.7,
        "decisiveness": 0.6,
        "aggression": 0.1,
        "supportiveness": 0.85,
        "adaptability": 0.6,
    }
    applied = SignalEngine.apply_signals(
        signals,
        "Collaborative",
        ["commander"],
        agents,
        graph,
        default_user_psych(),
        {"deadline_pressure": 50, "workload": 50, "project_stability": 50},
        default_hidden(),
    )
    edge = graph.get_edge("leader", "commander")
    assert edge.trust > 50
    assert agents["commander"]["internal_dynamic"]["stress"] < 60


def test_aggression_lowers_respect():
    graph = RelationshipGraph()
    graph.ensure_edge("leader", "commander", {"trust": 50, "respect": 50, "relationship": 50})
    agents = {
        "commander": {
            "static_params": {},
            "internal_dynamic": {"stress": 50, "confidence": 50, "fatigue": 30},
        }
    }
    signals = {
        "empathy": 0.2,
        "clarity": 0.3,
        "decisiveness": 0.4,
        "aggression": 0.8,
        "supportiveness": 0.2,
        "adaptability": 0.3,
    }
    SignalEngine.apply_signals(
        signals,
        "Directive",
        ["commander"],
        agents,
        graph,
        default_user_psych(),
        {"deadline_pressure": 50, "workload": 50, "project_stability": 50},
        default_hidden(),
    )
    edge = graph.get_edge("leader", "commander")
    assert edge.respect < 50
