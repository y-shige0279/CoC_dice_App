from models.config import DiceRule, Edition, load_config


def test_load_config_returns_config():
    config = load_config()

    assert "6th" in config.status
    assert "7th" in config.status


def test_load_config_converts_status_to_dice_rule():
    config = load_config()

    rule = config.status["6th"]["STR"]

    assert isinstance(rule, DiceRule)
    assert rule.count == 3
    assert rule.sides == 6
    assert rule.base == 0
    assert rule.multiplier == 1


def test_validate_edition_accepts_supported_edition():
    config = load_config()

    config.validate_edition(Edition.COC6)
    config.validate_edition(Edition.COC7)