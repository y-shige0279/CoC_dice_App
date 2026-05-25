import random
import json
from pathlib import Path
from datetime import datetime

# ログの保存用リスト
logs = []

MAX_REROLLS = 10000

# ダイスロール関数
def roll_dice(count, sides):
    total = 0
    for _ in range(count):
        total += random.randint(1, sides)
    return total

# 能力値の生成関数
def generate_status(editions):
    result ={}

    for status_name, rule in status[editions].items():
        count, sides, base, multiplier = rule
        result[status_name] = (roll_dice(count, sides) + base) * multiplier
    return result

# 能力値の条件を満たしているか確認
def check_total_conditions(result, editions):
    total = sum(result.values())
    return total >= target_total[editions]

def check_status_conditions(result, editions):
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

def check_conditions(result, editions):

    if not check_total_conditions(result, editions):
        return False

    if not check_status_conditions(result, editions):
        return False

    return True

def load_config():
    config_path = Path("config.json")
    
    if not config_path.exists():
        raise FileNotFoundError("config.json not found")
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_logs(logs):

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_path = log_dir / "result.log"

    with log_path.open(
        "a",
        encoding="utf-8"
    ) as f:

        for log in logs:
            f.write(f"{log}\n")

if __name__ == "__main__":
    result = {}
    total = 0
    reroll_cnt = 0
    
    config = load_config()
    status = config["status"]
    target_total = config["target_total"]
    target_status = config["target_status"]
    
    editions = input("Enter the edition (6th or 7th): ")
    
    if editions not in status:
        raise ValueError("Unsupported edition")
    
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
    
    save_logs(logs)