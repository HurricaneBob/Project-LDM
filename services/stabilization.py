"""Stabilization probability — deterministic, no LLM."""
import math

from config import Config


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def calculate_p_stabilize(
    mean_trust: float,
    mean_respect: float,
    mean_relationship: float,
    mean_stress: float,
    mean_fatigue: float,
    cohesion: float,
) -> float:
    x = (
        Config.STAB_W_TRUST * mean_trust
        + Config.STAB_W_RESPECT * mean_respect
        + Config.STAB_W_RELATIONSHIP * mean_relationship
        - Config.STAB_W_STRESS * mean_stress
        - Config.STAB_W_FATIGUE * mean_fatigue
        + Config.STAB_COHESION_BONUS * (cohesion / 100.0) * 50
        - 2.5
    )
    return round(sigmoid(x / 25.0), 4)


def is_stabilized(p_stabilize: float, threshold: float) -> bool:
    return p_stabilize >= threshold
