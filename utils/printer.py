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

    # ロールログの表示
    if SHOW_LOGS:
        print("Logs of rerolls")
        for log in character.logger.logs:
            print(log)