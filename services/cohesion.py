"""Team cohesion from leader-member relationships."""
from config import Config
from services.relationship_graph import RelationshipGraph


def calculate_cohesion(graph: RelationshipGraph, weights: dict | None = None) -> float:
    edges = graph.leader_edges()
    if not edges:
        return 50.0

    w = weights or {}
    wt = w.get("trust", Config.COHESION_W_TRUST)
    wr = w.get("respect", Config.COHESION_W_RESPECT)
    wrel = w.get("relationship", Config.COHESION_W_RELATIONSHIP)

    total = 0.0
    for e in edges:
        total += wt * e.trust + wr * e.respect + wrel * e.relationship

    return round(total / len(edges), 2)
