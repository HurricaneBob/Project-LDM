from models.extensions import db


class SessionAgent(db.Model):
    __tablename__ = "session_agents"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey("play_sessions.id"), nullable=False)
    agent_id = db.Column(db.String(36), db.ForeignKey("agents.id"), nullable=False)
    internal_dynamic = db.Column(db.JSON, nullable=False, default=dict)
    cpb_snapshot = db.Column(db.JSON, nullable=True)

    session = db.relationship("PlaySession", back_populates="session_agents")
    agent = db.relationship("Agent")
