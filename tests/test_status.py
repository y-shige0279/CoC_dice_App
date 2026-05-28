from models.status import StatusValue

def test_final_value_without_bonus():
    status = StatusValue(base=10)

    assert status.final_value() == 10


def test_final_value_with_bonus():
    status = StatusValue(base=10, bonus=3)

    assert status.final_value() == 13


def test_final_value_with_temp_bonus():
    status = StatusValue(base=10, temp_bonus=-2)

    assert status.final_value() == 8