from datetime import datetime, timezone

from models.extensions import db


class Turn(db.Model):
    __tablename__ = "turns"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey("play_sessions.id"), nullable=False)
    scenario_id = db.Column(db.String(36), db.ForeignKey("scenarios.id"), nullable=False)
    turn_index = db.Column(db.Integer, nullable=False)
    user_text = db.Column(db.Text, nullable=False)
    llm_summary = db.Column(db.Text, nullable=True)
    applied_delta = db.Column(db.JSON, nullable=True)
    cohesion = db.Column(db.Float, nullable=True)
    p_stabilize = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    session = db.relationship("PlaySession", back_populates="turns")
