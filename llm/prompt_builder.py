"""Build LLM prompts from llm_call_schemas.json."""
import json

from services.schema_loader import get_call_type, get_system_prompt


def _system_block() -> str:
    sp = get_system_prompt()
    rules = "\n".join(f"- {r}" for r in sp.get("core_rules", []))
    agents = sp.get("agents", {})
    agent_lines = "\n".join(
        f"- {name}: focus={info.get('focus', [])}" for name, info in agents.items()
    )
    return f"""ROLE: {sp.get('role', '')}
USER: {sp.get('user_role', '')}
RULES:
{rules}
AGENTS:
{agent_lines}
NOTE: {sp.get('parameter_note', '')}
"""


def build_call_prompt(call_type: str, payload: dict) -> str:
    ct = get_call_type(call_type)
    return f"""{_system_block()}

CALL_TYPE: {call_type}

INPUT (JSON):
{json.dumps(payload, indent=2)}

EXPECTED OUTPUT SCHEMA:
{json.dumps(ct.get('output_schema', {}), indent=2)}

Return ONLY valid JSON matching the output schema. No markdown.
"""
