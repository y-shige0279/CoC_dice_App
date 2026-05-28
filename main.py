import logging

from models.config import Edition, edition_map, load_config
from services.generator import generate_character
from utils.printer import print_result
from utils.inputter import input_bonuses
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

    logging.getLogger().setLevel(
        logging.DEBUG if config.debug else logging.INFO
    )

    editions = select_edition()
    
    # 先に補正を入力
    bonus_inputs = input_bonuses()

    # 補正情報を渡して生成
    character = generate_character(
        editions,
        config.status,
        config.target_total,
        config.target_status,
        bonus_inputs,
    )

    print_result(character)
    character.logger.save_all(character)

if __name__ == "__main__":
    run()