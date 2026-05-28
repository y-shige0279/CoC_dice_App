from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TypedDict

from models.config import BonusType, BonusHistory

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

# 能力値の合計を計算
def calculate_total_status(result: StatusResult) -> int:
    return sum(status.final_value() for status in result.values())

