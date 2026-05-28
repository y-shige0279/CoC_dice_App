import logging
from dataclasses import dataclass

from models.config import BonusType, Edition, SHOW_LOGS
from models.logger import RollLogger, RollLog
from models.status import StatusName, StatusResult, calculate_total_status

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