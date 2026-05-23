import random

# 能力値のロールダイス
status = {"STR": (3,6,0,1), 
          "CON": (3,6,0,1), 
          "POW": (3,6,0,1), 
          "DEX": (3,6,0,1), 
          "APP": (3,6,0,1), 
          "SIZ": (2,6,6,1), 
          "INT": (2,6,6,1), 
          "EDU": (3,6,3,1)
          }

# 能力値の条件値
target_total = 90

# 各能力値の条件値
target_status = {"STR": (10, 18),
                 "CON": (10, 18),
                 "POW": (10, 18),
                 "DEX": (10, 18),
                 "APP": (10, 18),
                 "SIZ": (13, 18),
                 "INT": (13, 18),
                 "EDU": (13, 21)
                }

# ダイスロール関数
def roll_dice(count, sides):
    total = 0
    for _ in range(count):
        total += random.randint(1, sides)
    return total

# 能力値の生成関数
def generate_status_6th():
    result ={}

    for status_name, rule in status.items():
        count, sides, base, multiplier = rule
        result[status_name] = (roll_dice(count, sides) + base) * multiplier
    return result

# 能力値の条件を満たしているか確認
def check_total_conditions(result):
    total = sum(result.values())
    return total >= target_total

def check_status_conditions(result):
    for status_name, (min_value, max_value) in target_status.items():
        if result[status_name] < min_value:
            return False
        if result[status_name] > max_value:
            return False
    return True

def check_conditions(result):

    if not check_total_conditions(result):
        return False

    if not check_status_conditions(result):
        return False

    return True

if __name__ == "__main__":
    result = {}
    total = 0
    
    while True:
        result = generate_status_6th()
        
        if check_conditions(result):
            break
        
    print("Call of Cthulhu 6th Edition Character Generator")
    print("Status:")

    for status_name, value in result.items():
        print(f"{status_name}: {value}")
    print("Total Status")
    total = sum(result.values())
    print(total)