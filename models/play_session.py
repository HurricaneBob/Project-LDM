import uuid
from datetime import datetime, timezone

from models.extensions import db


class PlaySession(db.Model):
    __tablename__ = "play_sessions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = db.Column(db.String(32), default="active")
    current_scenario_index = db.Column(db.Integer, default=1)
    current_scenario_id = db.Column(db.String(36), db.ForeignKey("scenarios.id"), nullable=True)
    turn_count = db.Column(db.Integer, default=0)
    last_dialogue = db.Column(db.JSON, nullable=True)
    situation_brief = db.Column(db.Text, nullable=True)
    user_psych = db.Column(db.JSON, nullable=True)
    environmental_state = db.Column(db.JSON, nullable=True)
    hidden_variables = db.Column(db.JSON, nullable=True)
    leadership_style_counts = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    session_agents = db.relationship("SessionAgent", back_populates="session", lazy=True)
    relationships = db.relationship("Relationship", back_populates="session", lazy=True)
    turns = db.relationship("Turn", back_populates="session", lazy=True)
    memories = db.relationship("Memory", back_populates="session", lazy=True)
    summaries = db.relationship("ScenarioSummary", back_populates="session", lazy=True)
