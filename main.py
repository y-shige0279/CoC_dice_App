import logging

from models.config import BonusType, Edition, edition_map, load_config
from models.status import StatusName
from services.generator import generate_character
from utils.printer import print_result
from utils.inputter import input_bonus
from utils.input_normalizer import normalize_input

# ロギングの設定
logging.basicConfig(level=logging.INFO)

def select_edition() -> Edition:
    while True:
        editions_input = normalize_input(
            input("どの版でキャラを作成しますか (6th or 7th): ")
        )

        if editions_input in edition_map:
            return edition_map[editions_input]

        print("存在しない版です。6 または 7 を入力してください。")

def run() -> None:
    config = load_config()

    editions = select_edition()

    character = generate_character(
        editions,
        config.status,
        config.target_total,
        config.target_status
    )

    while True:
        status_name, history_type, value, reason = input_bonus()

        character.apply_bonus(
            status_name,
            history_type=history_type,
            value=value,
            reason=reason,
        )

        continue_input = normalize_input(
            input("さらに補正を追加しますか？ (y/n): ")
)

        if continue_input not in {"y", "yes", "はい"}:
            break

    print_result(character)
    character.logger.save_logs()

if __name__ == "__main__":
    run()