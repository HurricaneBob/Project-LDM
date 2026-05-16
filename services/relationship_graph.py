"""Directed relationship graph for a session."""
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Edge:
    from_id: str
    to_id: str
    trust: float
    respect: float
    relationship: float

    def clamp(self):
        self.trust = max(0, min(100, self.trust))
        self.respect = max(0, min(100, self.respect))
        self.relationship = max(0, min(100, self.relationship))


class RelationshipGraph:
    LEADER_ID = "leader"

    def __init__(self, edges: List[Edge] | None = None):
        self._edges: Dict[Tuple[str, str], Edge] = {}
        if edges:
            for e in edges:
                self._edges[(e.from_id, e.to_id)] = e

    def get_edge(self, from_id: str, to_id: str) -> Edge | None:
        return self._edges.get((from_id, to_id))

    def ensure_edge(self, from_id: str, to_id: str, defaults: dict | None = None) -> Edge:
        key = (from_id, to_id)
        if key not in self._edges:
            d = defaults or {}
            self._edges[key] = Edge(
                from_id=from_id,
                to_id=to_id,
                trust=d.get("trust", 50.0),
                respect=d.get("respect", 50.0),
                relationship=d.get("relationship", 50.0),
            )
        return self._edges[key]

    def leader_edges(self) -> List[Edge]:
        return [e for (f, _), e in self._edges.items() if f == self.LEADER_ID]

    def agent_to_leader_edges(self) -> List[Edge]:
        return [e for (_, t), e in self._edges.items() if t == self.LEADER_ID]

    def apply_delta(
        self,
        from_id: str,
        to_id: str,
        trust: float = 0,
        respect: float = 0,
        relationship: float = 0,
    ):
        edge = self.ensure_edge(from_id, to_id)
        edge.trust += trust
        edge.respect += respect
        edge.relationship += relationship
        edge.clamp()

    def to_list(self) -> List[dict]:
        return [
            {
                "from_id": e.from_id,
                "to_id": e.to_id,
                "trust": round(e.trust, 2),
                "respect": round(e.respect, 2),
                "relationship": round(e.relationship, 2),
                "communication_quality": round(e.relationship, 2),
            }
            for e in self._edges.values()
        ]

    @classmethod
    def from_db_rows(cls, rows) -> "RelationshipGraph":
        edges = []
        for r in rows:
            comm = getattr(r, "communication_quality", None)
            rel = comm if comm is not None else r.relationship
            edges.append(
                Edge(
                    from_id=r.from_id,
                    to_id=r.to_id,
                    trust=r.trust,
                    respect=r.respect,
                    relationship=rel,
                )
            )
        return cls(edges)
