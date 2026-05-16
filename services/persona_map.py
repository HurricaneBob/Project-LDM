"""Map frontend personaId ↔ DB agent keys ↔ LLM speaking_agent names."""

PERSONA_TO_AGENT_KEY = {
    "commander": "commander",
    "facilitator": "facilitator",
    "strategist": "strategist",
    "supporter": "supporter",
    "adaptive": "adaptive",
    "Commander": "commander",
    "Facilitator": "facilitator",
    "Strategist": "strategist",
    "Supporter": "supporter",
    "Adaptive": "adaptive",
    "The Commander": "commander",
    "The Facilitator": "facilitator",
    "The Strategist": "strategist",
    "The Supporter": "supporter",
    "The Adaptive": "adaptive",
}

AGENT_KEY_TO_PERSONA_ID = {v: k for k, v in PERSONA_TO_AGENT_KEY.items() if k.islower()}


def to_persona_id(name_or_key: str) -> str:
    key = PERSONA_TO_AGENT_KEY.get(name_or_key, name_or_key.lower())
    return key if key in AGENT_KEY_TO_PERSONA_ID else name_or_key.lower()


def to_display_name(persona_id: str) -> str:
    from services.schema_loader import display_name_for_persona

    return display_name_for_persona(to_persona_id(persona_id))
