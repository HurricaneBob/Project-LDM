from models.extensions import db


class Relationship(db.Model):
    __tablename__ = "relationships"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey("play_sessions.id"), nullable=False)
    from_id = db.Column(db.String(64), nullable=False)
    to_id = db.Column(db.String(64), nullable=False)
    trust = db.Column(db.Float, default=50.0)
    respect = db.Column(db.Float, default=50.0)
    relationship = db.Column(db.Float, default=50.0)
    communication_quality = db.Column(db.Float, default=50.0)

    session = db.relationship("PlaySession", back_populates="relationships")

    __table_args__ = (
        db.UniqueConstraint("session_id", "from_id", "to_id", name="uq_rel_edge"),
    )
