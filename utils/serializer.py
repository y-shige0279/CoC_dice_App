# utils/serializer.py
from models.status import StatusResult

def serialize_result(result: StatusResult) -> dict:
    serialized = {}

    for status_name, value in result.items():
        serialized[status_name.value] = {
            "base": value.base,
            "bonus": value.bonus,
            "temp_bonus": value.temp_bonus,
            "history": value.history
        }

    return serialized