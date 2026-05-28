from models.config import BonusType
from models.status import StatusName
from utils.input_normalizer import normalize_input

def input_bonus() -> tuple[StatusName, BonusType, int, str]:
    permanent_words = {
        "恒久",
        "増加",
        "ぞうか",
        "増加分",
        "永久",
        "permanent",
        "p",
    }
    
    temporary_words = {
        "一時",
        "いちじてき",
        "一時的",
        "一時補正",
        "temporary",
        "temp",
        "t",
    }
    
    while True:
        try:
            status_input = normalize_input(
                input(
                    "能力値を入力してください "
                    "(STR/CON/POW/DEX/APP/SIZ/INT/EDU): ")
            ).upper()

            if status_input not in StatusName.__members__:
                raise ValueError("存在しない能力値です")

            bonus_type_input = normalize_input(
                input(
                    "補正タイプを入力してください "
                    "(恒久/増加分/一時): "
                )
            )


            if bonus_type_input in permanent_words:
                history_type = BonusType.PERMANENT

            elif bonus_type_input in temporary_words:
                history_type = BonusType.TEMPORARY

            else:
                raise ValueError("存在しない補正タイプです")

            value = int(normalize_input(input("補正値を入力してください:  ")))

            reason = input("補正理由を入力してください:")

            return (
                StatusName[status_input],
                history_type,
                value,
                reason,
            )
        
        except ValueError as error:
            print(f"入力エラー: {error}")
            print("もう一度入力してください。")
            
def input_bonuses() -> list[tuple[StatusName, BonusType, int, str]]:
    bonuses = []

    if not confirm_yes_no("補正を入力しますか？"):
        return bonuses

    while True:
        bonuses.append(input_bonus())

        if not confirm_yes_no("さらに補正を追加しますか？"):
            break

    return bonuses

def confirm_yes_no(message: str) -> bool:
    yes_words = {
        "y",
        "yes",
        "はい",
        "する",
        "追加",
        "追加する",
    }

    no_words = {
        "n",
        "no",
        "いいえ",
        "しない",
        "終了",
        "やめる",
    }

    while True:
        answer = normalize_input(
            input(f"{message} (y/n): ")
        )

        if answer in yes_words:
            return True

        if answer in no_words:
            return False

        print("y または n を入力してください。")