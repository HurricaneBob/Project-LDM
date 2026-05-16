import json
from pathlib import Path

from models.agent import Agent
from models.extensions import db
from models.scenario import Scenario
from models.scenario_agent import ScenarioAgent

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "seed_scenarios.json"


def seed_database(force: bool = False):
    if force:
        from models.memory import Memory
        from models.play_session import PlaySession
        from models.relationship import Relationship
        from models.scenario_summary import ScenarioSummary
        from models.session_agent import SessionAgent
        from models.turn import Turn

        Memory.query.delete()
        Turn.query.delete()
        Relationship.query.delete()
        SessionAgent.query.delete()
        ScenarioSummary.query.delete()
        PlaySession.query.delete()
        ScenarioAgent.query.delete()
        Scenario.query.delete()
        Agent.query.delete()
        db.session.commit()
    elif Scenario.query.first():
        return

    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    agent_by_key = {}
    for a in data["agents"]:
        agent = Agent(
            slug=a["key"],
            name=a["name"],
            role=a["role"],
            static_params=a["static_params"],
            cpb_profile=a["cpb_profile"],
        )
        db.session.add(agent)
        agent_by_key[a["key"]] = agent

    db.session.flush()

    for s in data["scenarios"]:
        scenario = Scenario(
            slug=s["slug"],
            title=s["title"],
            domain=s["domain"],
            sequence_index=s["sequence_index"],
            opening_situation=s["opening_situation"],
            stabilization_threshold=s.get("stabilization_threshold", 0.72),
            delta_weights=s.get("delta_weights", {}),
        )
        db.session.add(scenario)
        db.session.flush()
        for key in s["agent_keys"]:
            db.session.add(
                ScenarioAgent(scenario_id=scenario.id, agent_id=agent_by_key[key].id)
            )

    db.session.commit()
