"""Gemini client with mock mode and token logging."""
import json
import logging
from typing import Type, TypeVar

from pydantic import BaseModel

from config import Config

logger = logging.getLogger("ldm.llm")
T = TypeVar("T", bound=BaseModel)

_token_usage = {"calls": 0, "estimated_tokens": 0}


def get_token_usage() -> dict:
    return dict(_token_usage)


def _log_call(purpose: str, prompt_len: int):
    _token_usage["calls"] += 1
    _token_usage["estimated_tokens"] += prompt_len // 4
    logger.info("LLM call %s (~%d tokens est.)", purpose, prompt_len // 4)


def _mock_response(purpose: str) -> dict:
    mocks = {
        "1_game_init": {
            "selected_scenario": "Scenario 1",
            "situation_brief": "Deadline pressure is mounting. The Commander wants to ship now; the Strategist insists on one more risk review.",
        },
        "2_scenario_init": {
            "selected_scenario": "Scenario 2",
            "situation_brief": "Team dynamics are strained after a rushed call. Voices that were quiet before may stay silent without your intervention.",
        },
        "3A_semantic_analysis": {
            "communication_signals": {
                "empathy": 0.75,
                "clarity": 0.7,
                "decisiveness": 0.6,
                "aggression": 0.15,
                "supportiveness": 0.8,
                "adaptability": 0.65,
            },
            "leadership_style_tag": "Collaborative",
            "conflict_escalation_risk": "low",
        },
        "3B_dialogue_generation": {
            "narration": "The team exchanges glances, waiting to see if your message lands.",
            "lines": [
                {
                    "speaking_agent": "Commander",
                    "ai_response": "Good — let's lock priorities and move. What's the single next step?",
                },
                {
                    "speaking_agent": "Strategist",
                    "ai_response": "I can align with that if we document the trade-offs we are accepting.",
                },
            ],
        },
        "4_scenario_summary": {
            "scenario_outcome_summary": "The team stabilized enough to proceed, though underlying tension may resurface without follow-up."
        },
        "5_holistic_summary": {
            "holistic_results": {
                "parameter_deltas_analysis": "Empathy and clarity signals rose steadily across scenarios.",
                "leadership_pattern_summary": "Collaborative coaching dominated; directive bursts appeared under deadline stress.",
                "hr_competency_verdict": "Strong relational leadership with room to sharpen decisiveness under time pressure. SDG 8 alignment: decent work through inclusive team practices.",
            }
        },
        "memory": {"memory": "The leader validated concerns and clarified priorities, easing team stress."},
        "evaluation": {
            "leadership_analysis": "You demonstrated steady communication under pressure.",
            "strengths": ["Active listening", "Calm tone"],
            "weaknesses": ["Could delegate more explicitly"],
            "cohesion_impact": "Cohesion improved as trust rebuilt across scenarios.",
            "emotional_impact": "Team stress decreased when you validated concerns.",
            "dimension_scores": {
                "emotional_regulation": 7.5,
                "conflict_mediation": 7.0,
                "trust_building": 7.5,
                "adaptability": 6.5,
                "leadership_communication": 7.0,
            },
        },
        "classify": {
            "tone": "supportive",
            "targets": [],
            "intents": ["de_escalate"],
            "confidence": 0.9,
        },
        "dialogue": {
            "narration": "The team listens carefully.",
            "lines": [
                {
                    "speaking_agent": "Facilitator",
                    "ai_response": "Thanks for naming that — it helps us reset and focus.",
                }
            ],
            "turn_summary": "Team responded positively to supportive leadership.",
        },
        "opening": {
            "opening_narration": "The situation is tense as the team awaits your guidance.",
            "lines": [
                {
                    "speaking_agent": "Commander",
                    "ai_response": "We need clarity on priorities before we lose more time.",
                }
            ],
        },
    }
    return mocks.get(purpose, mocks.get("3B_dialogue_generation", {}))


def generate_json(
    purpose: str,
    prompt: str,
    schema: Type[T],
    model: str | None = None,
) -> T:
    _log_call(purpose, len(prompt))

    if Config.LLM_MOCK:
        data = _mock_response(purpose)
        return schema.model_validate(data)

    if not Config.GEMINI_API_KEY:
        data = _mock_response(purpose)
        logger.warning("No GEMINI_API_KEY; using mock for %s", purpose)
        return schema.model_validate(data)

    from google import genai

    client = genai.Client(api_key=Config.GEMINI_API_KEY)
    model = model or Config.GEMINI_MODEL_FLASH

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
        },
    )

    text = response.text or "{}"
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        cleaned = text.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(cleaned)

    return schema.model_validate(data)
