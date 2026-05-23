import random

# ログの保存用リスト
logs = []

MAX_REROLLS = 10000

# 能力値のロールダイス
status = {
        "6th": {
            "STR": (3,6,0,1), 
            "CON": (3,6,0,1), 
            "POW": (3,6,0,1), 
            "DEX": (3,6,0,1), 
            "APP": (3,6,0,1), 
            "SIZ": (2,6,6,1), 
            "INT": (2,6,6,1), 
            "EDU": (3,6,3,1)
            },
        "7th": {
            "STR": (3,6,0,5), 
            "CON": (3,6,0,5), 
            "POW": (3,6,0,5), 
            "DEX": (3,6,0,5), 
            "APP": (3,6,0,5), 
            "SIZ": (2,6,6,5), 
            "INT": (2,6,6,5), 
            "EDU": (2,6,6,5)
            }
}

# 能力値の条件値
target_total = {
    "6th": 90,
    "7th": 450
}

# 各能力値の条件値
target_status = {
                "6th": {
                    "STR": (10, 18),
                    "CON": (10, 18),
                    "POW": (10, 18),
                    "DEX": (10, 18),
                    "APP": (10, 18),
                    "SIZ": (13, 18),
                    "INT": (13, 18),
                    "EDU": (13, 21)
                },
                "7th": {
                    "STR": (50, 90),
                    "CON": (50, 90),
                    "POW": (50, 90),
                    "DEX": (50, 90),
                    "APP": (50, 90),
                    "SIZ": (65, 90),
                    "INT": (65, 90),
                    "EDU": (65, 90)
                }
}

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

if __name__ == "__main__":
    result = {}
    total = 0
    reroll_cnt = 0
    editions = "6th"
    
    if editions not in status:
        raise ValueError("Unsupported edition")
    
    while True:
        result = generate_status(editions)
        logs.append(result.copy())
        
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