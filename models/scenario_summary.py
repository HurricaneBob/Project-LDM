from datetime import datetime, timezone

from models.extensions import db


class ScenarioSummary(db.Model):
    __tablename__ = "scenario_summaries"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey("play_sessions.id"), nullable=False)
    scenario_id = db.Column(db.String(36), db.ForeignKey("scenarios.id"), nullable=False)
    turns_taken = db.Column(db.Integer, default=0)
    final_cohesion = db.Column(db.Float, nullable=True)
    final_p_stabilize = db.Column(db.Float, nullable=True)
    summary_text = db.Column(db.Text, nullable=True)
    parameter_evolution = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    session = db.relationship("PlaySession", back_populates="summaries")
