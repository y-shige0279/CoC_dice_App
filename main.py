import random

status = {"STR": (3,6,0, 1), 
          "CON": (3,6,0, 1), 
          "POW": (3,6,0, 1), 
          "DEX": (3,6,0, 1), 
          "APP": (3,6,0, 1), 
          "SIZ": (2,6,6, 1), 
          "INT": (2,6,6, 1), 
          "EDU": (3,6,3, 1)
          }


def roll_dice(count, sides):
    total = 0
    for _ in range(count):
        total += random.randint(1, sides)
    return total

def generate_status_6th():
    result ={}

    for status_name, rule in status.items():
        count, sides, base, multiplier = rule
        result[status_name] = (roll_dice(count, sides) + base) * multiplier
    return result

if __name__ == "__main__":
    print("Call of Cthulhu 6th Edition Character Generator")
    print("Status:")
    result = generate_status_6th()
    for status_name, value in result.items():
        print(f"{status_name}: {value}")
    print("Total Status")
    print(sum(result.values()))