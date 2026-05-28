# services/checker.py
from models.config import Edition
from models.status import StatusName, StatusResult, calculate_total_status

# 能力値の条件を満たしているか確認
def check_total_conditions(result: StatusResult, editions: Edition, target_total: dict[str, int]) -> bool:
    total = calculate_total_status(result)
    return total >= target_total[editions.value]

# 能力値ごとの条件を満たしているか確認
def check_status_conditions(result: StatusResult, editions: Edition, target_status: dict[str, dict[str, list[int]]]) -> bool:
    for status_name, (min_value, max_value) in target_status[editions.value].items():
        
        status_enum = StatusName(status_name)
        final_value = result[status_enum].final_value()
        
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
def check_conditions(result: StatusResult, editions: Edition, target_total: dict[str, int], target_status: dict[str, dict[str, list[int]]]) -> bool:

    if not check_total_conditions(result, editions, target_total):
        return False

    if not check_status_conditions(result, editions, target_status):
        return False

    return True