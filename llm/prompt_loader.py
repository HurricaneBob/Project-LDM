"""Load and format llm/prompts/*.txt templates."""
import json
from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

CALL_TYPE_TEMPLATES = {
    "1_game_init": "opening",
    "2_scenario_init": "opening",
    "3A_semantic_analysis": "semantic_analysis",
    "3B_dialogue_generation": "dialogue",
    "5_holistic_summary": "evaluation",
    "memory": "memory",
    "evaluation": "evaluation",
}


@lru_cache(maxsize=32)
def load_template(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return path.read_text(encoding="utf-8")


def template_for_call_type(call_type: str) -> str | None:
    return CALL_TYPE_TEMPLATES.get(call_type)


def format_template(name: str, **kwargs) -> str:
    """Format a template; missing keys become empty strings."""
    text = load_template(name)
    safe = {k: _stringify(v) for k, v in kwargs.items()}

    class _SafeDict(dict):
        def __missing__(self, key):
            return ""

    return text.format_map(_SafeDict(safe))


def _stringify(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2)
    return str(value)
