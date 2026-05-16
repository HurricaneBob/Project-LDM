import uuid

from models.extensions import db


class Scenario(db.Model):
    __tablename__ = "scenarios"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(64), nullable=False)
    sequence_index = db.Column(db.Integer, nullable=False)
    opening_situation = db.Column(db.Text, nullable=False)
    stabilization_threshold = db.Column(db.Float, default=0.72)
    delta_weights = db.Column(db.JSON, default=dict)
    cached_opening_narration = db.Column(db.Text, nullable=True)

    agents = db.relationship("ScenarioAgent", back_populates="scenario", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "domain": self.domain,
            "sequence_index": self.sequence_index,
            "opening_situation": self.opening_situation,
            "stabilization_threshold": self.stabilization_threshold,
        }
