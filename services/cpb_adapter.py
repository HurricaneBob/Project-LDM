"""Adapter between LDM simulation and Conceptual-Personality-Builder."""
import copy
import os
import sys
from typing import Any

from config import Config
from cpb_events.leadership_events import (
    apply_blaming_communication,
    apply_neutral_update,
    apply_supportive_clarification,
)

CPB_ROOT = Config.CPB_PATH
if CPB_ROOT not in sys.path:
    sys.path.insert(0, CPB_ROOT)

from Aditional.PersonalInformation import PersonalInformation  # noqa: E402
from PersonalityAtributes.Character import Character  # noqa: E402
from PersonalityAtributes.EmotionalStyle import EmotionalStyle  # noqa: E402
from PersonalityAtributes.Environment import Environment  # noqa: E402
from PersonalityAtributes.HabitualBehavior import HabitualBehavior  # noqa: E402
from PersonalityAtributes.InternalNeeds import InternalNeeds  # noqa: E402
from PersonalityAtributes.LifeExperience import LifeExperience  # noqa: E402
from PersonalityAtributes.Motivations import Motivations  # noqa: E402
from PersonalityAtributes.SelfConcept import SelfConcept  # noqa: E402
from PersonalityAtributes.SelfEsteem import SelfEsteem  # noqa: E402
from PersonalityAtributes.Temperament import Temperament  # noqa: E402
from PersonalityAtributes.ThoughtPatterns import ThoughtPatterns  # noqa: E402
from PersonalityBuilder.PersonalityBuilder import PersonalityBuilder  # noqa: E402

DEFAULT_PERSONAL_INFO = {
    "name": "Team Member",
    "age": 28,
    "birth_date": "1996-01-01",
    "gender": "Non-binary",
    "nationality": "Unknown",
    "residence": "Remote",
    "marital_status": "Single",
    "current_occupation": "Team Member",
    "academic_level": "Bachelor's Degree",
    "language": "English",
    "hobbies": ["collaboration"],
    "pets": [],
    "practical_skills": ["communication"],
    "climate_preference": "Temperate",
    "color_preference": "Blue",
    "place_preference": "Urban",
    "phobia": "None",
}


def _merge_defaults(profile: dict, section: str, defaults: dict) -> dict:
    base = copy.deepcopy(defaults)
    base.update(profile.get(section, {}))
    return base


def build_from_profile(profile: dict) -> PersonalityBuilder:
    """Build PersonalityBuilder from seed/cpb_profile dict."""
    pi = _merge_defaults(profile, "personal_info", DEFAULT_PERSONAL_INFO)
    personal_info = PersonalInformation(**pi)

    char = _merge_defaults(
        profile,
        "character",
        {
            "discipline": 65,
            "responsibility": 65,
            "morality": 70,
            "empathy": 60,
            "social_norm_adaptation": 60,
            "perseverance": 65,
        },
    )
    character = Character(**char)

    es_data = _merge_defaults(
        profile,
        "emotional_style",
        {
            "emotional_reactivity": 55,
            "emotional_stability": 55,
            "emotional_recovery_time": 50,
            "empathy_level": 60,
            "emotional_expressiveness": 60,
            "rejection_sensitivity": 50,
        },
    )
    emotional_style = EmotionalStyle(**es_data)

    environment = Environment(
        environment_stability=profile.get("environment", {}).get("environment_stability", 60),
        socioeconomic_level=60,
        family_influence=65,
        social_support=60,
        cultural_norm_influence=55,
        education_level=profile.get("environment", {}).get("education_level", 3),
        emotional_environment_quality=65,
        significant_events=[],
        community_type=3,
        diversity_exposure=55,
    )

    habitual_behavior = HabitualBehavior(
        sociability_level=65,
        dominance_assertiveness=55,
        discipline_level=65,
        behavioral_impulsivity=45,
        communication_style=4,
        cooperation_level=70,
        reliability_level=70,
        decision_making=4,
        lifestyle=4,
        time_management=70,
        risk_seeking_level=50,
    )

    internal_needs = InternalNeeds(
        emotional_security=60,
        connection_affection=65,
        autonomy=65,
        competence=70,
        stimulation=55,
        order_structure=70,
        purpose_meaning=75,
        personal_reaffirmation=70,
    )

    le = _merge_defaults(
        profile,
        "life_experience",
        {
            "positive_experiences": [],
            "negative_experiences": [],
            "accumulated_emotional_impact": 50,
            "key_relationships": [],
            "major_achievements": [],
            "failures": [],
            "major_challenges": [],
            "learned_resilience_level": 55,
            "acquired_values": [],
            "experience_based_beliefs": [],
            "unresolved_trauma_level": 25,
        },
    )
    life_experience = LifeExperience(**le)

    motivations = Motivations(
        achievement_motivation=70,
        affiliation_motivation=65,
        power_motivation=55,
        security_motivation=70,
        autonomy_motivation=65,
        exploration_motivation=60,
        recognition_motivation=65,
        transcendence_motivation=55,
    )

    sc = _merge_defaults(
        profile,
        "self_concept",
        {
            "self_image_clarity": 65,
            "internal_coherence": 65,
            "general_self_efficacy": 65,
            "locus_of_control": 60,
            "self_image_consistency": 70,
            "behavior": 70,
        },
    )
    self_concept = SelfConcept(**sc)

    se_data = _merge_defaults(
        profile,
        "self_esteem",
        {
            "global_self_esteem": 60,
            "emotional_self_esteem": 60,
            "social_self_esteem": 60,
            "physical_self_esteem": 60,
            "academic_work_self_esteem": 65,
            "self_esteem_stability": 65,
        },
    )
    self_esteem = SelfEsteem(**se_data)

    temp = _merge_defaults(
        profile,
        "temperament",
        {
            "energy_level": 65,
            "emotional_sensitivity": 55,
            "impulsivity": 50,
            "stimulation_seeking": 60,
            "emotional_stability": 60,
        },
    )
    temperament = Temperament(**temp)

    thought_patterns = ThoughtPatterns(
        interpretation_style=4,
        cognitive_flexibility=65,
        cognitive_biases=[],
        rationality_level=70,
        thinking_style=4,
        cognitive_speed=65,
        cognitive_complexity=65,
        self_criticism=55,
    )

    return PersonalityBuilder(
        character,
        emotional_style,
        environment,
        habitual_behavior,
        internal_needs,
        life_experience,
        motivations,
        self_concept,
        self_esteem,
        temperament,
        thought_patterns,
        personal_info,
    )


def snapshot_to_dict(pb: PersonalityBuilder) -> dict:
    """Serialize CPB state to JSON-storable dict."""
    return {
        "character": {
            "discipline": pb.character.get_discipline(),
            "responsibility": pb.character.get_responsibility(),
            "perseverance": pb.character.get_perseverance(),
            "empathy": pb.character.get_empathy(),
        },
        "emotional_style": {
            "emotional_reactivity": pb.emotional_style.get_emotional_reactivity(),
            "emotional_stability": pb.emotional_style.get_emotional_stability(),
            "rejection_sensitivity": pb.emotional_style.get_rejection_sensitivity(),
        },
        "self_esteem": {"global_self_esteem": pb.self_esteem.get_global_self_esteem()},
        "self_concept": {
            "general_self_efficacy": pb.self_concept.get_general_self_efficacy()
        },
        "temperament": {
            "energy_level": pb.temperament.get_energy_level(),
            "emotional_sensitivity": pb.temperament.get_emotional_sensitivity(),
        },
        "life_experience": {
            "learned_resilience_level": pb.life_experience.learned_resilience_level,
            "positive_experiences": list(pb.life_experience.positive_experiences)[-5:],
            "negative_experiences": list(pb.life_experience.negative_experiences)[-5:],
        },
        "personal_info": {"name": pb.personal_information.name},
    }


def dict_to_profile(snapshot: dict) -> dict:
    """Convert snapshot back to cpb_profile for rebuild."""
    return snapshot


def get_modifiers(pb: PersonalityBuilder) -> dict:
    """Map CPB traits to simulation modifiers."""
    return {
        "patience": (
            100 - pb.temperament.get_emotional_sensitivity() * 0.5
            + pb.character.get_perseverance() * 0.5
        )
        / 2,
        "resilience": (
            pb.life_experience.learned_resilience_level
            + pb.character.get_perseverance()
        )
        / 2,
        "experience": pb.self_concept.get_general_self_efficacy(),
        "stress_reactivity": pb.emotional_style.get_emotional_reactivity(),
        "rejection_sensitivity": pb.emotional_style.get_rejection_sensitivity(),
    }


def apply_leadership_event(pb: PersonalityBuilder, tone: str, magnitude: float = 1.0):
    if tone in ("supportive", "encouraging", "validating"):
        return apply_supportive_clarification(pb, magnitude)
    if tone in ("blaming", "dismissive", "aggressive"):
        return apply_blaming_communication(pb, magnitude)
    return apply_neutral_update(pb, magnitude)
