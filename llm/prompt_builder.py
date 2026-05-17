"""Build LLM prompts from llm/prompts/*.txt templates and llm_call_schemas.json."""
import json

from llm.prompt_loader import format_template, template_for_call_type
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


def _payload_to_template_vars(call_type: str, payload: dict) -> dict:
    """Map JSON payloads to .txt template placeholder names."""
    if call_type in ("1_game_init", "2_scenario_init"):
        agents = payload.get("active_agents", [])
        if isinstance(agents, list):
            agents = "\n".join(f"- {a}" for a in agents)
        return {
            "situation": payload.get("scenario_context_summary")
            or f"Scenario {payload.get('scenario_id', 1)}",
            "agents": agents,
        }

    if call_type == "3A_semantic_analysis":
        agents = payload.get("active_agents", [])
        if isinstance(agents, list):
            agents = ", ".join(str(a) for a in agents)
        return {
            "user_input": payload.get("user_input", ""),
            "active_agents": agents,
            "scenario_context_summary": payload.get("scenario_context_summary", ""),
        }

    if call_type == "3B_dialogue_generation":
        compressed = payload.get("compressed_state", {})
        return {
            "situation": payload.get("scenario_context_summary", ""),
            "state_snapshot": json.dumps(compressed, indent=2),
            "memories": json.dumps(compressed.get("memory_summary", []), indent=2),
            "last_dialogue": payload.get("last_dialogue", ""),
            "user_message": payload.get("user_message", ""),
            "tone": payload.get("tone", "neutral"),
        }

    if call_type == "memory":
        return {
            "tone": payload.get("tone", ""),
            "user_message": payload.get("user_message", ""),
            "applied_delta": payload.get("applied_delta", ""),
        }

    if call_type in ("5_holistic_summary", "evaluation"):
        memories = payload.get("memories", [])
        if isinstance(memories, list):
            memories = "\n".join(f"- {m}" for m in memories)
        summaries = payload.get("scenario_summaries", "")
        if isinstance(summaries, dict):
            summaries = json.dumps(summaries, indent=2)
        trends = payload.get("trends") or payload.get("global_parameter_deltas", "")
        style_dist = payload.get("leadership_style_distribution")
        if isinstance(trends, dict) or isinstance(style_dist, dict):
            trends = json.dumps(
                {
                    "global_parameter_deltas": trends,
                    "leadership_style_distribution": style_dist or {},
                },
                indent=2,
            )
        return {
            "scenario_summaries": summaries,
            "trends": trends,
            "memories": memories or "No memories recorded yet.",
        }

    return {k: v for k, v in payload.items()}


def build_call_prompt(call_type: str, payload: dict, scenario_prefix: str = "") -> str:
    ct = get_call_type(call_type)
    output_schema = ct.get("output_schema", {})

    template_name = template_for_call_type(call_type)
    if template_name:
        vars_ = _payload_to_template_vars(call_type, payload)
        body = format_template(template_name, **vars_)
    else:
        body = f"CALL_TYPE: {call_type}\n\nINPUT (JSON):\n{json.dumps(payload, indent=2)}"

    prefix = f"{scenario_prefix}\n\n" if scenario_prefix else ""
    return f"""{_system_block()}

{prefix}{body}

EXPECTED OUTPUT SCHEMA:
{json.dumps(output_schema, indent=2)}

Return ONLY valid JSON matching the output schema. No markdown.
"""
