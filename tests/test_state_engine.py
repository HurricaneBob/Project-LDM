from services.relationship_graph import RelationshipGraph
from services.state_engine import StateEngine
from services.stabilization import calculate_p_stabilize, is_stabilized


def test_supportive_increases_trust():
    graph = RelationshipGraph()
    graph.ensure_edge("leader", "a1", {"trust": 50, "respect": 50, "relationship": 50})
    agents = {
        "a1": {
            "static_params": {"patience": 60, "resilience": 60, "experience": 50},
            "internal_dynamic": {"stress": 60, "confidence": 45, "fatigue": 30, "emotion": "tense"},
        }
    }
    applied = StateEngine.apply_communication(
        "supportive", ["a1"], agents, graph, {}, None
    )
    edge = graph.get_edge("leader", "a1")
    assert edge.trust > 50
    assert agents["a1"]["internal_dynamic"]["stress"] < 60


def test_blaming_decreases_trust():
    graph = RelationshipGraph()
    graph.ensure_edge("leader", "a1", {"trust": 50, "respect": 50, "relationship": 50})
    agents = {
        "a1": {
            "static_params": {"patience": 50, "resilience": 50, "experience": 50},
            "internal_dynamic": {"stress": 50, "confidence": 50, "fatigue": 30, "emotion": "neutral"},
        }
    }
    StateEngine.apply_communication("blaming", ["a1"], agents, graph, {}, None)
    edge = graph.get_edge("leader", "a1")
    assert edge.trust < 50
    assert agents["a1"]["internal_dynamic"]["stress"] > 50


def test_p_stabilize_monotonic_with_trust():
    low = calculate_p_stabilize(40, 50, 50, 60, 40, 45)
    high = calculate_p_stabilize(80, 50, 50, 60, 40, 45)
    assert high > low


def test_stabilization_threshold():
    assert is_stabilized(0.75, 0.72)
    assert not is_stabilized(0.70, 0.72)
