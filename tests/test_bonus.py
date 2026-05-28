from models.config import BonusType
from models.status import StatusValue


def test_apply_permanent_bonus():
    status = StatusValue(base=10)

    status.apply_bonus(
        history_type=BonusType.PERMANENT,
        value=3,
        reason="HO補正",
    )

    assert status.bonus == 3
    assert status.temp_bonus == 0
    assert status.final_value() == 13


def test_apply_temporary_bonus():
    status = StatusValue(base=10)

    status.apply_bonus(
        history_type=BonusType.TEMPORARY,
        value=-2,
        reason="負傷",
    )

    assert status.bonus == 0
    assert status.temp_bonus == -2
    assert status.final_value() == 8


def test_bonus_history_is_added():
    status = StatusValue(base=10)

    status.apply_bonus(
        history_type=BonusType.PERMANENT,
        value=5,
        reason="成長",
    )

    assert len(status.history) == 1
    assert status.history[0]["type"] == "permanent"
    assert status.history[0]["value"] == 5
    assert status.history[0]["reason"] == "成長"