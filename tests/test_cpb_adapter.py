import pytest

from services.cpb_adapter import build_from_profile, get_modifiers, snapshot_to_dict


@pytest.fixture
def sample_profile():
    return {
        "character": {"perseverance": 80, "empathy": 70},
        "emotional_style": {"emotional_reactivity": 60, "emotional_stability": 55},
        "temperament": {"emotional_sensitivity": 50, "energy_level": 65},
        "self_esteem": {"global_self_esteem": 70},
        "self_concept": {"general_self_efficacy": 75},
        "life_experience": {"learned_resilience_level": 72},
        "personal_info": {"name": "Test Agent", "current_occupation": "Engineer"},
    }


def test_build_and_snapshot(sample_profile):
    pb = build_from_profile(sample_profile)
    snap = snapshot_to_dict(pb)
    mods = get_modifiers(pb)
    assert snap["personal_info"]["name"] == "Test Agent"
    assert 0 <= mods["patience"] <= 100
    assert mods["resilience"] > 0
