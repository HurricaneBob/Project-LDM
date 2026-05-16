"""Load llm_call_schemas.json once at startup."""
import json
from functools import lru_cache
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "data" / "llm_call_schemas.json"

SCENARIO_AGENT_KEYS = {
    1: ["commander", "strategist"],
    2: ["facilitator", "supporter"],
    3: ["commander", "strategist"],
    4: ["supporter"],
    5: ["facilitator", "adaptive"],
}


@lru_cache(maxsize=1)
def load_schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_system_prompt() -> dict:
    return load_schema().get("system_prompt", {})


def get_call_type(name: str) -> dict:
    return load_schema().get("call_types", {}).get(name, {})


def get_backend_state_schema() -> dict:
    return load_schema().get("backend_state_schema", {})


def active_agents_for_scenario(scenario_index: int) -> list[str]:
    return SCENARIO_AGENT_KEYS.get(scenario_index, ["commander", "strategist"])


def display_name_for_persona(persona_key: str) -> str:
    names = {
        "commander": "Commander",
        "facilitator": "Facilitator",
        "strategist": "Strategist",
        "supporter": "Supporter",
        "adaptive": "Adaptive",
    }
    return names.get(persona_key, persona_key.title())
