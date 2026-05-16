"""Map communication signals to frontend HR competency parameterDeltas."""

SIGNAL_TO_PARAMS = {
    "empathy": ["Empathy", "Emotional Awareness", "Psychological Safety"],
    "clarity": ["Communication Style", "Decision-Making", "Analytical Thinking"],
    "decisiveness": ["Decision-Making", "Execution Speed", "Leadership Tendencies"],
    "aggression": ["Conflict Resolution", "Stress Management"],
    "supportiveness": ["Team Motivation", "Inclusive Communication", "Psychological Safety"],
    "adaptability": ["Cultural Adaptability", "Communication Flexibility", "Situational Awareness"],
}

STYLE_TO_PARAMS = {
    "Directive": ["Decision-Making", "Execution Speed", "Leadership Tendencies"],
    "Collaborative": ["Communication Style", "Team Motivation", "Conflict Resolution"],
    "Avoidant": ["Stress Management"],
    "Delegative": ["Leadership Tendencies", "Situational Awareness"],
    "Coaching": ["Empathy", "Psychological Safety", "Inclusive Communication"],
}


def signals_to_parameter_deltas(signals: dict, leadership_style: str | None = None) -> dict:
    deltas: dict[str, int] = {}

    for signal_name, params in SIGNAL_TO_PARAMS.items():
        val = float(signals.get(signal_name, 0))
        if val < 0.35:
            continue
        bump = 1 if val < 0.65 else 2
        for p in params:
            deltas[p] = deltas.get(p, 0) + bump

    if leadership_style and leadership_style in STYLE_TO_PARAMS:
        for p in STYLE_TO_PARAMS[leadership_style]:
            deltas[p] = deltas.get(p, 0) + 1

    aggression = float(signals.get("aggression", 0))
    if aggression > 0.5:
        for p in ["Conflict Resolution", "Stress Management"]:
            deltas[p] = deltas.get(p, 0) - 1

    return {k: v for k, v in deltas.items() if v != 0}
