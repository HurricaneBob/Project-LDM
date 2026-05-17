"""Load seed_scenarios.json and llm_call_schemas.json for runtime prompts."""
import json
from functools import lru_cache
from pathlib import Path

from llm.prompt_builder import build_call_prompt
from services.persona_map import to_display_name

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SEED_PATH = DATA_DIR / "seed_scenarios.json"


@lru_cache(maxsize=1)
def load_seed_data() -> dict:
    with open(SEED_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_scenario(sequence_index: int) -> dict | None:
    for s in load_seed_data().get("scenarios", []):
        if s.get("sequence_index") == sequence_index:
            return s
    return None


def get_agent_by_key(key: str) -> dict | None:
    for a in load_seed_data().get("agents", []):
        if a.get("key") == key:
            return a
    return None


def get_agents_for_scenario(scenario: dict) -> list[dict]:
    keys = scenario.get("agent_keys", [])
    out = []
    for key in keys:
        agent = get_agent_by_key(key)
        if agent:
            out.append(agent)
    return out


def scenario_context_block(sequence_index: int) -> str:
    """Human-readable scenario + agent parameters from seed_scenarios.json."""
    scenario = get_scenario(sequence_index)
    if not scenario:
        return ""

    agents = get_agents_for_scenario(scenario)
    agent_lines = []
    for a in agents:
        static = a.get("static_params", {})
        agent_lines.append(
            f"- {a.get('name', a.get('key'))} ({a.get('role', '')}): "
            f"static_params={json.dumps(static)}"
        )

    weights = scenario.get("delta_weights", {})
    return f"""SCENARIO CONTEXT (from seed_scenarios.json):
Title: {scenario.get('title', '')}
Situation: {scenario.get('opening_situation', '')}
Domain: {scenario.get('domain', '')}
Stabilization threshold: {scenario.get('stabilization_threshold', '')}
Signal delta weights: {json.dumps(weights)}
Active agents:
{chr(10).join(agent_lines)}
"""


def build_prompt(call_type: str, payload: dict, scenario_index: int | None = None) -> str:
    """Prompt from llm_call_schemas + prompts/*.txt + optional seed scenario block."""
    prefix = scenario_context_block(scenario_index) if scenario_index else ""
    return build_call_prompt(call_type, payload, scenario_prefix=prefix)


def display_names_for_keys(persona_keys: list[str]) -> list[str]:
    return [to_display_name(k) for k in persona_keys]
