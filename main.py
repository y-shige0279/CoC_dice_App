import random
import json
from pathlib import Path
from datetime import datetime



MAX_REROLLS = 10000

# ダイスロール関数
def roll_dice(count: int, sides: int) -> int:
    total = 0
    for _ in range(count):
        total += random.randint(1, sides)
    return total

# 能力値の生成関数
def generate_status(editions: str) -> dict:
    result ={}

    for status_name, rule in status[editions].items():
        count, sides, base, multiplier = rule
        result[status_name] = (roll_dice(count, sides) + base) * multiplier
    return result

# キャラクター生成関数
def generate_character(editions: str) -> tuple[dict, int, list]:
    reroll_cnt = 0
    # ログの保存用リスト
    logs = []

    while True:
        result = generate_status(editions)
        logs.append(
            {
                "timestamp": datetime.now().isoformat(),
                "result": result.copy()
            }
        )
        
        if check_conditions(result, editions):
            break
        reroll_cnt += 1
        
        if reroll_cnt >= MAX_REROLLS:
            print("Maximum number of rerolls reached. Exiting.")
            break
    return result, reroll_cnt, logs

# 能力値の条件を満たしているか確認
def check_total_conditions(result: dict, editions: str) -> bool:
    total = sum(result.values())
    return total >= target_total[editions]

# 能力値ごとの条件を満たしているか確認
def check_status_conditions(result: dict, editions: str) -> bool:
    for status_name, (min_value, max_value) in target_status[editions].items():
        if min_value > max_value:
            raise ValueError(
                f"{status_name}: min_value > max_value"
            )
        if result[status_name] < min_value:
            return False
        if result[status_name] > max_value:
            return False
    return True

# 条件をすべて満たしているか確認
def check_conditions(result: dict, editions: str) -> bool:

    if not check_total_conditions(result, editions):
        return False

    if not check_status_conditions(result, editions):
        return False

    return True

# 設定ファイルの読み込み
def load_config() -> dict:
    config_path = Path("config.json")
    
    if not config_path.exists():
        raise FileNotFoundError("config.json not found")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)

# ログの保存
def save_logs(logs: list, editions: str):

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
    )

    log_logpath = log_dir / f"{timestamp}_{editions}_result.log"
    log_jsonpath = log_dir / f"{timestamp}_{editions}_result.json"

    with log_logpath.open(
        "a",
        encoding="utf-8"
    ) as f:

        for log in logs:
            f.write(f"{log}\n")
            
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

# 結果の表示
def print_result(result: dict, reroll_cnt: int, editions: str, logs: list):
    print(f"Call of Cthulhu {editions} Edition Character Generator")
    print("Status:")

    for status_name, value in result.items():
        print(f"{status_name}: {value}")
    
    print("Total Status")
    total = sum(result.values())
    print(total)
    
    print("Number of rerolls")
    print(reroll_cnt)
    print("Logs of rerolls")
    for log in logs:
        print(log)

if __name__ == "__main__":
    result = {}
    reroll_cnt = 0
    
    config = load_config()
    status = config["status"]
    target_total = config["target_total"]
    target_status = config["target_status"]
    
    editions = input("Enter the edition (6th or 7th): ")
    
    if editions not in status:
        raise ValueError("Unsupported edition")
    
    result, reroll_cnt, logs = generate_character(editions)
    print_result(result, reroll_cnt, editions, logs)
    save_logs(logs, editions)