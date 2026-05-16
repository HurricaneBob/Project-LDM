"""Scenario loading and progression."""
from models.extensions import db
from models.scenario import Scenario
from models.scenario_agent import ScenarioAgent
from models.scenario_summary import ScenarioSummary


class ScenarioManager:
    @staticmethod
    def get_by_id(scenario_id: str) -> Scenario | None:
        return db.session.get(Scenario, scenario_id)

    @staticmethod
    def get_by_index(sequence_index: int) -> Scenario | None:
        return Scenario.query.filter_by(sequence_index=sequence_index).first()

    @staticmethod
    def get_agents_for_scenario(scenario_id: str):
        links = ScenarioAgent.query.filter_by(scenario_id=scenario_id).all()
        return [link.agent for link in links]

    @staticmethod
    def complete_scenario(
        session_id: str,
        scenario: Scenario,
        turns_taken: int,
        final_cohesion: float,
        final_p: float,
        parameter_evolution: dict,
    ):
        summary = ScenarioSummary(
            session_id=session_id,
            scenario_id=scenario.id,
            turns_taken=turns_taken,
            final_cohesion=final_cohesion,
            final_p_stabilize=final_p,
            summary_text=(
                f"Completed {scenario.title} in {turns_taken} turns. "
                f"Final cohesion {final_cohesion:.1f}, stabilization {final_p:.2f}."
            ),
            parameter_evolution=parameter_evolution,
        )
        db.session.add(summary)
        db.session.flush()
        return summary

    @staticmethod
    def next_scenario(current_index: int) -> Scenario | None:
        return Scenario.query.filter_by(sequence_index=current_index + 1).first()
