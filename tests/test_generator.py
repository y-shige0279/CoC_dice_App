from services.generator import generate_character
from models.config import load_config, Edition


def test_generate_character_returns_character():
    config = load_config()

    character = generate_character(
        Edition.COC6,
        config.status,
        config.target_total,
        config.target_status,
        [],
    )

    assert character is not None


def test_generated_character_has_status():
    config = load_config()

    character = generate_character(
        Edition.COC6,
        config.status,
        config.target_total,
        config.target_status,
        [],
    )

    assert "STR" in [
        status_name.value
        for status_name in character.status.keys()
    ]


def test_generated_character_matches_total_condition():
    config = load_config()

    character = generate_character(
        Edition.COC6,
        config.status,
        config.target_total,
        config.target_status,
        [],
    )

    total = sum(
        status.final_value()
        for status in character.status.values()
    )

    assert total >= config.target_total["6th"]