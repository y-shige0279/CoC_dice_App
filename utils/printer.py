from models.character import Character
from models.config import SHOW_LOGS
from models.status import calculate_total_status

# 結果の表示
def print_result(character: Character) -> None:
    print(f"Call of Cthulhu {character.edition.value} Edition Character Generator")
    print("Status:")

    for status_name, value in character.status.items():
        final_value = value.final_value()
        print(f"{status_name.value}: "
              f"{final_value}"
              f" (Base: {value.base}, "
              f"Bonus: {value.bonus}, "
              f"Temp Bonus: {value.temp_bonus})"
              )

    print("Total Status")
    print("※ 条件判定は補正後の値で行っています")
    total = calculate_total_status(character.status)
    print(total)

    print("Number of rerolls")
    print(character.reroll_cnt)
    
    has_history = any(
    value.history
    for value in character.status.values()
    )

    if has_history:
        # 能力値の履歴の表示
        print("補正一覧")
        for status_name, value in character.status.items():

            if not value.history:
                continue

            print(f"{status_name.value}:")

            for history in value.history:
                type_name = (
                    "増加分"
                    if history["type"] == "permanent"
                else "一時"
                )

                print(
                    f"  - {history['value']:+} "
                    f"({type_name}) "
                    f": {history['reason']}"
                )

    # ロールログの表示
    if SHOW_LOGS:
        print("Logs of rerolls")
        for log in character.logger.logs:
            print(log)