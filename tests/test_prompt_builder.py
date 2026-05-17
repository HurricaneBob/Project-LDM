"""Verify LLM prompts include .txt templates and JSON output schemas."""
import json

from llm.prompt_builder import build_call_prompt
from llm.prompt_loader import load_template


def test_opening_template_in_game_init():
    prompt = build_call_prompt(
        "1_game_init",
        {"scenario_id": 1, "active_agents": ["Commander", "Strategist"]},
    )
    assert "opening_narration" in load_template("opening") or "Return JSON" in load_template("opening")
    assert "situation_brief" in prompt
    assert "EXPECTED OUTPUT SCHEMA" in prompt


def test_semantic_analysis_template():
    prompt = build_call_prompt(
        "3A_semantic_analysis",
        {
            "user_input": "Let's align on priorities.",
            "active_agents": ["Commander"],
            "scenario_context_summary": "Deadline pressure.",
        },
    )
    assert "communication_signals" in prompt
    assert "Let's align on priorities." in prompt
    assert "Deadline pressure." in prompt


def test_dialogue_template():
    prompt = build_call_prompt(
        "3B_dialogue_generation",
        {
            "user_message": "I hear your concerns.",
            "compressed_state": {"memory_summary": ["Prior tension eased."]},
            "tone": "Collaborative",
            "last_dialogue": "commander: We need a decision.",
            "scenario_context_summary": "Team under pressure.",
        },
    )
    assert "Leader just said" in load_template("dialogue") or "user_message" in prompt
    assert "I hear your concerns." in prompt
    assert "EXPECTED OUTPUT SCHEMA" in prompt


def test_memory_template():
    prompt = build_call_prompt(
        "memory",
        {"tone": "supportive", "user_message": "Thanks team.", "applied_delta": "{}"},
    )
    assert "memory" in prompt.lower()
    assert "Thanks team." in prompt


def test_evaluation_template():
    prompt = build_call_prompt(
        "evaluation",
        {
            "scenario_summaries": {"scenario_1": "Stable outcome."},
            "trends": '{"trust": "up"}',
            "memories": ["Leader validated concerns."],
        },
    )
    assert "leadership_analysis" in prompt
    assert "Stable outcome." in prompt


def test_seed_scenario_context_in_build_prompt():
    from services.json_context import build_prompt, get_scenario

    scenario = get_scenario(1)
    assert scenario is not None
    prompt = build_prompt(
        "3A_semantic_analysis",
        {
            "user_input": "We need to ship tonight.",
            "active_agents": ["Commander", "Strategist"],
            "scenario_context_summary": scenario["opening_situation"][:100],
        },
        scenario_index=1,
    )
    assert "seed_scenarios.json" in prompt
    assert "Time Pressure" in prompt or scenario["title"] in prompt
    assert scenario["opening_situation"][:40] in prompt


def test_scenario_summary_uses_json_fallback():
    prompt = build_call_prompt(
        "4_scenario_summary",
        {
            "scenario_id": 1,
            "parameter_deltas": {"Empathy": 2},
            "final_exchange_summary": "Team aligned.",
        },
    )
    assert "scenario_outcome_summary" in prompt
    assert json.dumps({"Empathy": 2}) in prompt or "Empathy" in prompt
