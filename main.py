import logging

from models.config import BonusType, Edition, edition_map, load_config
from models.status import StatusName
from services.generator import generate_character
from utils.printer import print_result

# ロギングの設定
logging.basicConfig(level=logging.INFO)

def select_edition() -> Edition:
    editions_input = input("Enter the edition (6th or 7th): ").lower()
    if editions_input not in edition_map:
        raise ValueError("Unsupported edition")
    return edition_map[editions_input]

def apply_default_bonuses(character) -> None:
    character.apply_bonus(
        StatusName.STR,
        history_type=BonusType.PERMANENT,
        value=5,
        reason="職業補正",
    )

    character.apply_bonus(
        StatusName.STR,
        history_type=BonusType.TEMPORARY,
        value=-10,
        reason="負傷",
    )

def run() -> None:
    config = load_config()

    editions = select_edition()

    character = generate_character(
        editions,
        config.status,
        config.target_total,
        config.target_status
    )

    apply_default_bonuses(character)

    print_result(character)
    character.logger.save_logs()

if __name__ == "__main__":
    run()