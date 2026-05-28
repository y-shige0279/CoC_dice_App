from models.character import Character
from models.status import calculate_total_status

def serialize_character(character: Character) -> dict:
    serialized_status = {}

    for status_name, value in character.status.items():
        serialized_status[status_name.value] = {
            "base": value.base,
            "bonus": value.bonus,
            "temp_bonus": value.temp_bonus,
            "final": value.final_value(),
            "history": value.history,
        }

    return {
        "edition": character.edition.value,
        "reroll_count": character.reroll_cnt,
        "total_status": calculate_total_status(character.status),
        "status": serialized_status,
    }