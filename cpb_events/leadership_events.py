"""Simulation-owned CPB mutators for leadership communication events."""


def apply_supportive_clarification(personality_builder, magnitude: float = 1.0):
    es = personality_builder.emotional_style
    se = personality_builder.self_esteem
    delta = 2.0 * magnitude
    es.set_emotional_stability(min(100, es.get_emotional_stability() + delta))
    es.set_emotional_reactivity(max(0, es.get_emotional_reactivity() - delta * 0.5))
    se.set_global_self_esteem(min(100, se.get_global_self_esteem() + delta * 0.5))
    personality_builder.life_experience.positive_experiences.append(
        "Leader provided supportive clarification under pressure."
    )
    return "Supportive clarification applied."


def apply_blaming_communication(personality_builder, magnitude: float = 1.0):
    es = personality_builder.emotional_style
    se = personality_builder.self_esteem
    delta = 3.0 * magnitude
    es.set_emotional_stability(max(0, es.get_emotional_stability() - delta))
    es.set_emotional_reactivity(min(100, es.get_emotional_reactivity() + delta * 0.7))
    se.set_global_self_esteem(max(0, se.get_global_self_esteem() - delta * 0.6))
    personality_builder.life_experience.negative_experiences.append(
        "Leader used blaming communication during crisis."
    )
    return "Blaming communication applied."


def apply_neutral_update(personality_builder, magnitude: float = 0.5):
    return "Neutral communication noted."
