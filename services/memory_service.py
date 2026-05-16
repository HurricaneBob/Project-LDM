"""Compressed semantic memory storage."""
from config import Config
from models.extensions import db
from models.memory import Memory


class MemoryService:
    @staticmethod
    def add(session_id: str, text: str, agent_id: str | None = None, memory_type: str = "semantic"):
        mem = Memory(
            session_id=session_id,
            agent_id=agent_id,
            text=text,
            memory_type=memory_type,
        )
        db.session.add(mem)
        db.session.flush()
        return mem

    @staticmethod
    def get_recent(session_id: str, limit: int | None = None) -> list[str]:
        limit = limit or Config.MAX_MEMORIES_IN_PROMPT
        rows = (
            Memory.query.filter_by(session_id=session_id)
            .order_by(Memory.created_at.desc())
            .limit(limit)
            .all()
        )
        return [m.text for m in reversed(rows)]

    @staticmethod
    def should_extract(tone: str, applied_delta: dict) -> bool:
        high_risk = tone in ("blaming", "aggressive", "Directive", "high")
        supportive = tone in ("supportive", "encouraging", "validating", "Collaborative", "Coaching")
        if high_risk or supportive:
            return True
        for agent_delta in applied_delta.get("per_agent", {}).values():
            if abs(agent_delta.get("trust_delta", 0)) >= Config.MEMORY_TRUST_DELTA_THRESHOLD:
                return True
        return False
