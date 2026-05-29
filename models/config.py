import json
import logging
import sys
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import TypedDict

MAX_REROLLS = 10000 # 最大リロール回数
SHOW_LOGS = False # ログを表示するかどうか

def get_resource_path(filename: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / filename

    return Path(filename)

# エディションの定義
class Edition(Enum):
    COC6 = "6th"
    COC7 = "7th"
    
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
    
"""
# 能力値の条件の型定義
class StatusCondition:
    min: int
    max: int
"""

# 能力値のダイスルールの型定義
@dataclass
class DiceRule:
    count: int
    sides: int
    base: int
    multiplier: int

# ログの型定義
@dataclass
class Config:
    debug: bool
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
    
    
# 設定ファイルの読み込み
def load_config() -> Config:
    config_path = get_resource_path("config.json")
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
            debug=data.get("debug", False),
            status=status_config,
            target_total=data["target_total"],
            target_status=data["target_status"]
        )
    