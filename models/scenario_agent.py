from models.extensions import db


class ScenarioAgent(db.Model):
    __tablename__ = "scenario_agents"

    scenario_id = db.Column(db.String(36), db.ForeignKey("scenarios.id"), primary_key=True)
    agent_id = db.Column(db.String(36), db.ForeignKey("agents.id"), primary_key=True)

    scenario = db.relationship("Scenario", back_populates="agents")
    agent = db.relationship("Agent")
