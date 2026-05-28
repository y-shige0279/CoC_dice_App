# utils/dice.py
import random

# ダイスロール関数
def roll_dice(count: int, sides: int) -> int:
    total = 0
    for _ in range(count):
        total += random.randint(1, sides)
    return total