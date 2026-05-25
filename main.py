import random
import json
from pathlib import Path
from datetime import datetime
import logging
from enum import Enum
from typing import TypedDict
import copy

# ロギングの設定
logging.basicConfig(level=logging.INFO)

MAX_REROLLS = 10000 # 最大リロール回数
SHOW_LOGS = False # ログを表示するかどうか

# エディションの定義
class Edition(Enum):
    COC6 = "6th"
    COC7 = "7th"
    
# 能力値の名前の定義
class StatusName(Enum):
    STR = "STR"
    CON = "CON"
    POW = "POW"
    DEX = "DEX"
    APP = "APP"
    SIZ = "SIZ"
    INT = "INT"
    EDU = "EDU"
    
# 能力値補正の履歴の型定義
class BonusHistory(TypedDict):
    type: str
    value: int
    reason: str
    timestamp: str
    
# 能力値の型定義
class StatusValue(TypedDict):
    base: int
    bonus: int
    temp_bonus: int
    history: list[BonusHistory] # 能力値の変化履歴
    
type StatusResult = dict[StatusName, StatusValue]

# ロールログの型定義
class RollLog(TypedDict):
    timestamp: str
    result: StatusResult
    
# ログの型定義
class Config(TypedDict):
    status: dict[StatusName, dict[str, list[int]]]
    target_total: dict[StatusName, int]
    target_status: dict[StatusName, dict[str, list[int]]]
    
edition_map = {
    "6th": Edition.COC6,
    "coc6": Edition.COC6,
    "6": Edition.COC6,
    "7th": Edition.COC7,
    "coc7": Edition.COC7,
    "7": Edition.COC7
}

# ダイスロール関数
def roll_dice(count: int, sides: int) -> int:
    total = 0
    for _ in range(count):
        total += random.randint(1, sides)
    return total

# 能力値の生成関数
def generate_status(editions: Edition) -> StatusResult:
    result: StatusResult = {}

    for status_name, rule in status[editions.value].items():
        count, sides, base, multiplier = rule
        result[status_name] = {
            "base": (roll_dice(count, sides) + base) * multiplier,
            "bonus": 0,
            "temp_bonus": 0,
            "history": []
        }
    return result

# キャラクター生成関数
def generate_character(editions: Edition) -> tuple[StatusResult, int, list[RollLog]]:
    reroll_cnt = 0
    # ログの保存用リスト
    logs = []

    while True:
        result = generate_status(editions)
        logs.append(
            {
                "timestamp": datetime.now().isoformat(),
                "result": copy.deepcopy(result)
            }
        )
        
        if check_conditions(result, editions):
            break
        reroll_cnt += 1
        
        if reroll_cnt % 100 == 0:
            logging.debug(f"Reroll count: {reroll_cnt}")
        
        if reroll_cnt >= MAX_REROLLS:
            logging.info("Maximum number of rerolls reached. Exiting.")
            break
    return result, reroll_cnt, logs

# 能力値の最終値を計算
def calculate_final_status(
    status_data: StatusValue
) -> int:
    return (
        status_data["base"]
        + status_data["bonus"]
        + status_data["temp_bonus"]
    )
    
# 能力値補正を設定
def apply_bonus(
    result: StatusResult,
    status_name: StatusName,
    bonus: int = 0,
    temp_bonus: int = 0,
    reason: str = ""
) -> None:
    
    # 能力値の存在確認
    if status_name not in result:
        raise ValueError(f"Unknown status: {status_name}")
    
    before = calculate_final_status(
        result[status_name]
    )
    logging.info(
    f"Apply bonus: {status_name} "
    f"(bonus={bonus}, temp_bonus={temp_bonus})"
    )
    result[status_name]["bonus"] += bonus
    result[status_name]["temp_bonus"] += temp_bonus
    
    if reason:
        result[status_name]["history"].append(
            {
                "type": "bonus",
                "value": bonus,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    final_value = calculate_final_status(
    result[status_name]
    )

    if final_value < 0:
        raise ValueError(f"Final value for {status_name} is negative")
    
    after = final_value
    logging.info(
    f"{status_name} changed "
    f"from {before} to {after}"
)

def apply_bonuses(
    result: StatusResult,
    bonuses: dict[str, int]
):
    for status_name, value in bonuses.items():
        apply_bonus(
            result,
            status_name,
            bonus=value
        )

def calculate_total_status(
    result: StatusResult
) -> int:
    return sum(calculate_final_status(status_data) for status_data in result.values())

# 能力値の条件を満たしているか確認
def check_total_conditions(result: StatusResult, editions: Edition) -> bool:
    total = calculate_total_status(result)
    return total >= target_total[editions.value]

# 能力値ごとの条件を満たしているか確認
def check_status_conditions(result: StatusResult, editions: Edition) -> bool:
    for status_name, (min_value, max_value) in target_status[editions.value].items():
        
        final_value = calculate_final_status(
            result[status_name]
            )
        
        if min_value > max_value:
            raise ValueError(
                f"{status_name}: min_value > max_value"
            )
        if final_value < min_value:
            return False
        if final_value > max_value:
            return False
    return True

# 条件をすべて満たしているか確認
def check_conditions(result: StatusResult, editions: Edition) -> bool:

    if not check_total_conditions(result, editions):
        return False

    if not check_status_conditions(result, editions):
        return False

    return True

# 設定ファイルの読み込み
def load_config() -> Config:
    config_path = Path("config.json")
    logging.info(f"Loading config: {config_path}")
    
    if not config_path.exists():
        raise FileNotFoundError("config.json not found")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)

# ログの保存
def save_logs(logs: list[RollLog], editions: Edition) -> None:

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
    )

    log_logpath = log_dir / f"{timestamp}_{editions.value}_result.log"
    log_jsonpath = log_dir / f"{timestamp}_{editions.value}_result.json"

    with log_logpath.open(
        "a",
        encoding="utf-8"
    ) as f:

        for log in logs:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")
            
    with log_jsonpath.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            logs,
            f,
            ensure_ascii=False,
            indent=4
        )
    
    logging.info(f"Saved log file: {log_logpath}")
    logging.info(f"Saved json file: {log_jsonpath}")

# 結果の表示
def print_result(result: StatusResult, reroll_cnt: int, editions: Edition, logs: list[RollLog]):
    print(f"Call of Cthulhu {editions.value} Edition Character Generator")
    print("Status:")

    for status_name, value in result.items():
        final_value = calculate_final_status(
                value
            )
        print(f"{status_name}: "
              f"{final_value}"
              f" (Base: {value['base']}, "
              f"Bonus: {value['bonus']}, "
              f"Temp Bonus: {value['temp_bonus']})"
              )
    
    print("Total Status")
    total = calculate_total_status(result)
    print(total)
    
    print("Number of rerolls")
    print(reroll_cnt)
    
    # ロールログの表示
    if SHOW_LOGS:
        print("Logs of rerolls")
        for log in logs:
            print(log)

if __name__ == "__main__":
    result: StatusResult = {}
    reroll_cnt: int = 0
    logs: list[RollLog] = []

    config = load_config()
    status = config["status"]
    target_total = config["target_total"]
    target_status = config["target_status"]
    
    editions_input = input("Enter the edition (6th or 7th): ").lower()
    if editions_input not in edition_map:
        raise ValueError("Unsupported edition")

    editions = edition_map[editions_input]
    if editions.value not in status:
        raise ValueError("Unsupported edition")
    

    result, reroll_cnt, logs = generate_character(editions)
    # 永続補正
    apply_bonus(
    result,
    StatusName.STR,
    bonus=5,
    reason="職業補正"
)

    # 一時補正
    apply_bonus(result, StatusName.STR, temp_bonus=-10)

    print_result(result, reroll_cnt, editions, logs)
    save_logs(logs, editions)