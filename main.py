import random
import json
from pathlib import Path
from datetime import datetime
import logging
from enum import Enum
from typing import TypedDict
import copy
from dataclasses import dataclass, field

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
    
# 能力値補正の種類の定義
class BonusType(Enum):
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    
# 能力値補正の履歴の型定義
class BonusHistory(TypedDict):
    type: str
    value: int
    reason: str
    timestamp: str
    
@dataclass
class DiceRule:
    count: int
    sides: int
    base: int
    multiplier: int
    
# 能力値の型定義
@dataclass
class StatusValue:
    base: int
    bonus: int = 0
    temp_bonus: int = 0
    history: list[BonusHistory] = field(default_factory=list) # 補正履歴の初期値は空のリスト

    # 能力値の最終値を計算
    def final_value(self) -> int:
        return (
            self.base
            + self.bonus
            + self.temp_bonus
        )
        
    # 能力値補正を適用
    def apply_bonus(
        self,
        history_type: BonusType,
        value: int,
        reason: str = ""
    ) -> None:

        if history_type == BonusType.PERMANENT:
            self.bonus += value

        elif history_type == BonusType.TEMPORARY:
            self.temp_bonus += value

        if reason:
            self.history.append(
                {
                    "type": history_type.value,
                    "value": value,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                }
            )

        if self.final_value() < 0:
            raise ValueError("Final value is negative")
    
StatusResult = dict[StatusName, StatusValue]

# ロールログの型定義
class RollLog(TypedDict):
    timestamp: str
    result: StatusResult
    
@dataclass
class RollLogger:
    edition: Edition
    logs: list[RollLog] = field(default_factory=list)
    
    def add_log(self, result: StatusResult) -> None:
        self.logs.append(
            {
                "timestamp": datetime.now().isoformat(),
                "result": copy.deepcopy(result)
            }
        )
        
    def add_roll(self, result: StatusResult) -> None:
        self.add_log(result)
        logging.debug(f"Added log for {self.edition.value} edition")
        
    # ログの保存
    def save_logs(self) -> None:

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
        )

        log_logpath = log_dir / f"{timestamp}_{self.edition.value}_result.log"
        log_jsonpath = log_dir / f"{timestamp}_{self.edition.value}_result.json"

        with log_logpath.open(
            "a",
            encoding="utf-8"
        ) as f:

            for log in self.logs:
                serialized_log = {
                    "timestamp": log["timestamp"],
                    "result": serialize_result(log["result"])
                }

                f.write(json.dumps(serialized_log, ensure_ascii=False) + "\n")

        with log_jsonpath.open(
            "w",
            encoding="utf-8"
        ) as f:

            serialized_logs = []

            for log in self.logs:
                serialized_logs.append(
                    {
                    "timestamp": log["timestamp"],
                    "result": serialize_result(log["result"])
                    }
                )

            json.dump(
                serialized_logs,
                f,
                ensure_ascii=False,
                indent=4
            )

        logging.info(f"Saved log file: {log_logpath}")
        logging.info(f"Saved json file: {log_jsonpath}")

    
# ログの型定義
@dataclass
class Config:
    status: dict[str, dict[str, DiceRule]]
    target_total: dict[str, int]
    target_status: dict[str, dict[str, list[int]]]
    
    def validate_edition(self, editions: Edition) -> None:
        if editions.value not in self.status:
            raise ValueError("Unsupported edition")
    
edition_map = {
    "6th": Edition.COC6,
    "coc6": Edition.COC6,
    "6": Edition.COC6,
    "7th": Edition.COC7,
    "coc7": Edition.COC7,
    "7": Edition.COC7
}
@dataclass
class Character:
    logger: RollLogger
    edition: Edition
    status: StatusResult
    reroll_cnt: int = 0
    
    # 能力値補正を設定
    def apply_bonus(
        self,
        status_name: StatusName,
        history_type: BonusType,
        value: int = 0,
        reason: str = "",
    ) -> None:

        # 能力値の存在確認
        if status_name not in self.status:
            raise ValueError(f"Unknown status: {status_name}")

        before = self.status[status_name].final_value()

        logging.info(
        f"Apply bonus: {status_name.value} "
        f"(type={history_type.value}, value={value})"
        )

        self.status[status_name].apply_bonus(
            history_type=history_type,
            value=value,
            reason=reason
        )

        after = self.status[status_name].final_value()
        logging.info(
        f"{status_name.name} changed "
        f"from {before} to {after}"
        )
        
    # 結果の表示
    def print_result(self):
        print(f"Call of Cthulhu {self.edition.value} Edition Character Generator")
        print("Status:")

        for status_name, value in self.status.items():
            final_value = value.final_value()
            print(f"{status_name.value}: "
                  f"{final_value}"
                  f" (Base: {value.base}, "
                  f"Bonus: {value.bonus}, "
                  f"Temp Bonus: {value.temp_bonus})"
                  )

        print("Total Status")
        total = calculate_total_status(self.status)
        print(total)

        print("Number of rerolls")
        print(self.reroll_cnt)

        # ロールログの表示
        if SHOW_LOGS:
            print("Logs of rerolls")
            for log in self.logger.logs:
                print(log)

# ダイスロール関数
def roll_dice(count: int, sides: int) -> int:
    total = 0
    for _ in range(count):
        total += random.randint(1, sides)
    return total

# 能力値の生成関数
def generate_status(editions: Edition, status_config: dict[str, dict[str, DiceRule]]) -> StatusResult:
    result: StatusResult = {}

    for status_name, rule in status_config[editions.value].items():
        status_enum = StatusName(status_name)
        
        result[status_enum] = StatusValue(
            base=(
                roll_dice(rule.count, rule.sides)
                + rule.base
            ) * rule.multiplier
        )
    return result

# キャラクター生成関数
def generate_character(editions: Edition, status_config: dict[str, dict[str, DiceRule]],
                       target_total: dict[str, int], target_status: dict[str, dict[str, list[int]]]) -> Character:
    reroll_cnt = 0
    logger = RollLogger(edition=editions)
    
    while True:
        # 能力値を生成
        result = generate_status(editions, status_config)
        # ログに生成結果を追加
        logger.add_roll(result)
        
        if check_conditions(result, editions, target_total, target_status):
            break
        reroll_cnt += 1
        
        if reroll_cnt % 100 == 0:
            logging.debug(f"Reroll count: {reroll_cnt}")
        
        if reroll_cnt >= MAX_REROLLS:
            logging.info("Maximum number of rerolls reached. Exiting.")
            break
    
    character = Character(
        logger=logger,
        status=result,
        edition=editions,
        reroll_cnt=reroll_cnt,
    )
    return character

def apply_bonuses(
    character: Character,
    bonuses: dict[StatusName, int]
):
    for status_name, value in bonuses.items():
        character.apply_bonus(
            status_name,
            history_type=BonusType.PERMANENT,
            value=value
        )
        
# 能力値の合計を計算
def calculate_total_status(result: StatusResult) -> int:
    return sum(status.final_value() for status in result.values())

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

# 設定ファイルの読み込み
def load_config() -> Config:
    config_path = Path("config.json")
    logging.info(f"Loading config: {config_path}")
    
    if not config_path.exists():
        raise FileNotFoundError("config.json not found")
    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
        status_config = {}

        for edition, statuses in data["status"].items():
            status_config[edition] = {}

            for status_name, rule in statuses.items():
                status_config[edition][status_name] = DiceRule(
                    count=rule[0],
                    sides=rule[1],
                    base=rule[2],
                    multiplier=rule[3],
                )
        return Config(
            status=status_config,
            target_total=data["target_total"],
            target_status=data["target_status"]
        )
    
    
def serialize_result(result: StatusResult) -> dict:
    serialized = {}

    for status_name, value in result.items():
        serialized[status_name.value] = {
            "base": value.base,
            "bonus": value.bonus,
            "temp_bonus": value.temp_bonus,
            "history": value.history
        }

    return serialized

if __name__ == "__main__":
    character: Character | None = None
    logs: list[RollLog] = []

    config = load_config()
    status = config.status
    target_total = config.target_total
    target_status = config.target_status
    editions_input = input("Enter the edition (6th or 7th): ").lower()
    if editions_input not in edition_map:
        raise ValueError("Unsupported edition")

    editions = edition_map[editions_input]
    config.validate_edition(editions)

    character = generate_character(editions, status, target_total, target_status)
    
    # 永続補正
    character.apply_bonus(
    StatusName.STR,
    history_type=BonusType.PERMANENT,
    value=5,
    reason="職業補正",
)

    # 一時補正
    character.apply_bonus(StatusName.STR, history_type=BonusType.TEMPORARY, value=-10, reason="負傷")

    character.print_result()
    character.logger.save_logs()