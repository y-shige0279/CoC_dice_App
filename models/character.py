import logging
from dataclasses import dataclass

from models.config import BonusType, Edition
from models.logger import RollLogger
from models.status import StatusName, StatusResult

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

        logging.debug(
        f"Apply bonus: {status_name.value} "
        f"(type={history_type.value}, value={value})"
        )

        self.status[status_name].apply_bonus(
            history_type=history_type,
            value=value,
            reason=reason
        )

        after = self.status[status_name].final_value()
        logging.debug(
        f"{status_name.name} changed "
        f"from {before} to {after}"
        )