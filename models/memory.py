from datetime import datetime, timezone

from models.extensions import db


class Memory(db.Model):
    __tablename__ = "memories"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey("play_sessions.id"), nullable=False)
    agent_id = db.Column(db.String(36), db.ForeignKey("agents.id"), nullable=True)
    text = db.Column(db.Text, nullable=False)
    memory_type = db.Column(db.String(32), default="semantic")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    session = db.relationship("PlaySession", back_populates="memories")
