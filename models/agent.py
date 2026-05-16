import uuid

from models.extensions import db


class Agent(db.Model):
    __tablename__ = "agents"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    static_params = db.Column(db.JSON, nullable=False, default=dict)
    cpb_profile = db.Column(db.JSON, nullable=False, default=dict)
    cpb_snapshot = db.Column(db.JSON, nullable=True)

    def to_public_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "static_params": self.static_params,
        }
