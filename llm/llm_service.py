import json

from config import Config
from llm.gemini_client import generate_json
from llm.prompt_builder import build_call_prompt
from llm.schemas import (
    DialogueGenerationResponse,
    DialogueLine,
    FinalEvaluation,
    GameInitResponse,
    HolisticSummaryResponse,
    MemoryExtract,
    ScenarioInitResponse,
    ScenarioSummaryResponse,
    SemanticAnalysisResponse,
)
from services.persona_map import to_display_name, to_persona_id


class LLMService:
    @staticmethod
    def game_init(scenario_id: int, active_agents: list[str]) -> GameInitResponse:
        payload = {
            "scenario_id": scenario_id,
            "active_agents": [to_display_name(a) for a in active_agents],
            "scenario_context_summary": f"Scenario {scenario_id} initialization",
        }
        prompt = build_call_prompt("1_game_init", payload)
        return generate_json("1_game_init", prompt, GameInitResponse)

    @staticmethod
    def scenario_init(
        scenario_id: int,
        active_agents: list[str],
        compressed_state: dict,
    ) -> ScenarioInitResponse:
        payload = {
            "scenario_id": scenario_id,
            "active_agents": [to_display_name(a) for a in active_agents],
            "compressed_state": compressed_state,
            "scenario_context_summary": compressed_state.get("memory_summary", [""])[0]
            if compressed_state.get("memory_summary")
            else f"Scenario {scenario_id}",
        }
        prompt = build_call_prompt("2_scenario_init", payload)
        return generate_json("2_scenario_init", prompt, ScenarioInitResponse)

    @staticmethod
    def semantic_analysis(
        user_input: str,
        active_agents: list[str],
        scenario_context_summary: str,
    ) -> SemanticAnalysisResponse:
        payload = {
            "user_input": user_input,
            "active_agents": [to_display_name(a) for a in active_agents],
            "scenario_context_summary": scenario_context_summary,
        }
        prompt = build_call_prompt("3A_semantic_analysis", payload)
        return generate_json("3A_semantic_analysis", prompt, SemanticAnalysisResponse)

    @staticmethod
    def dialogue_generation(
        active_agents: list[str],
        compressed_state: dict,
        user_input: str,
        max_speakers: int = 3,
        scenario_context_summary: str = "",
        tone: str = "neutral",
        last_dialogue: str = "",
    ) -> DialogueGenerationResponse:
        payload = {
            "active_agents": [to_display_name(a) for a in active_agents],
            "compressed_state": compressed_state,
            "user_message": user_input,
            "max_speakers": max_speakers,
            "scenario_context_summary": scenario_context_summary,
            "tone": tone,
            "last_dialogue": last_dialogue,
        }
        prompt = build_call_prompt("3B_dialogue_generation", payload)
        prompt += f"\nReturn JSON with 'lines' array of up to {max_speakers} objects: speaking_agent, ai_response. Optional narration string."
        result = generate_json("3B_dialogue_generation", prompt, DialogueGenerationResponse)
        if not result.lines:
            result.lines = [
                DialogueLine(
                    speaking_agent=to_display_name(active_agents[0]),
                    ai_response="We need your direction on this before we can move forward.",
                )
            ]
        return result

    @staticmethod
    def scenario_summary(
        scenario_id: int,
        parameter_deltas: dict,
        final_exchange_summary: str,
    ) -> ScenarioSummaryResponse:
        payload = {
            "scenario_id": scenario_id,
            "parameter_deltas": parameter_deltas,
            "final_exchange_summary": final_exchange_summary,
        }
        prompt = build_call_prompt("4_scenario_summary", payload)
        return generate_json("4_scenario_summary", prompt, ScenarioSummaryResponse)

    @staticmethod
    def holistic_summary(
        scenario_summaries: dict,
        global_parameter_deltas: dict,
        leadership_style_distribution: dict,
    ) -> HolisticSummaryResponse:
        payload = {
            "scenario_summaries": scenario_summaries,
            "global_parameter_deltas": global_parameter_deltas,
            "leadership_style_distribution": leadership_style_distribution,
        }
        prompt = build_call_prompt("5_holistic_summary", payload)
        return generate_json(
            "5_holistic_summary",
            prompt,
            HolisticSummaryResponse,
            model=Config.GEMINI_MODEL_EVAL,
        )

    @staticmethod
    def extract_memory(tone: str, user_message: str, applied_delta: str) -> str:
        payload = {"tone": tone, "user_message": user_message, "applied_delta": applied_delta}
        prompt = build_call_prompt("memory", payload)
        result = generate_json("memory", prompt, MemoryExtract)
        return result.memory

    @staticmethod
    def classify_communication(situation: str, agents: list[dict], user_message: str):
        """Legacy wrapper for /api/scenario/interact."""
        from llm.schemas import CommunicationClassification

        analysis = LLMService.semantic_analysis(
            user_message,
            [a.get("id", a.get("name", "")) for a in agents],
            situation[:300],
        )
        tone = "supportive" if analysis.communication_signals.supportiveness > 0.6 else "neutral"
        if analysis.communication_signals.aggression > 0.5:
            tone = "blaming"
        return CommunicationClassification(
            tone=tone,
            targets=[a["id"] for a in agents],
            intents=["de_escalate"],
            confidence=0.85,
        )

    @staticmethod
    def generate_opening(situation: str, agents: list[dict]):
        from llm.schemas import OpeningResponse

        keys = [a.get("id", "commander") for a in agents]
        init = LLMService.game_init(1, keys)
        lines = [
            {"agent_id": keys[0], "name": agents[0].get("name", ""), "line": init.situation_brief[:200]}
        ]
        return OpeningResponse(opening_narration=init.situation_brief, lines=lines)

    @staticmethod
    def generate_dialogue(
        situation: str,
        state_snapshot: str,
        memories: list,
        last_dialogue: str,
        user_message: str,
        tone: str,
    ):
        from llm.schemas import DialogueResponse

        compressed = {"memory_summary": memories}
        if state_snapshot:
            try:
                compressed.update(json.loads(state_snapshot))
            except json.JSONDecodeError:
                compressed["state_snapshot"] = state_snapshot

        dlg = LLMService.dialogue_generation(
            ["commander"],
            compressed,
            user_message,
            max_speakers=2,
            scenario_context_summary=situation[:300],
            tone=tone,
            last_dialogue=last_dialogue,
        )
        lines = [
            {"agent_id": to_persona_id(l.speaking_agent), "name": l.speaking_agent, "line": l.ai_response}
            for l in dlg.lines
        ]
        return DialogueResponse(
            narration=dlg.narration,
            lines=lines,
            turn_summary=tone,
        )

    @staticmethod
    def final_evaluation(scenario_summaries: str, trends: str, memories: list):
        return LLMService.final_evaluation_legacy(scenario_summaries, trends, memories)

    @staticmethod
    def final_evaluation_legacy(
        scenario_summaries: str, trends: str, memories: list[str]
    ) -> FinalEvaluation:
        summaries = scenario_summaries
        if isinstance(summaries, str):
            try:
                summaries = json.loads(summaries)
            except json.JSONDecodeError:
                summaries = {"summary": scenario_summaries}

        payload = {
            "scenario_summaries": summaries,
            "trends": trends,
            "memories": memories,
        }
        prompt = build_call_prompt("evaluation", payload)
        return generate_json("evaluation", prompt, FinalEvaluation)
