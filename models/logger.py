from __future__ import annotations

import copy
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from models.config import Edition
from models.status import StatusResult
from utils.serializer import serialize_result

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
    def save_logs(self, timestamp: str) -> None:

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

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
        
    def save_character(
        self,
        character: "Character",
        timestamp: str
    ) -> None:
        from utils.character_serializer import serialize_character

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        character_path = (
            log_dir
            / f"{timestamp}_{self.edition.value}_character.json"
        )

        with character_path.open(
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                serialize_character(character),
                f,
                ensure_ascii=False,
                indent=4,
            )

        logging.info(
            f"Saved character file: {character_path}"
        )
        
    def save_all(self, character: "Character") -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.save_logs(timestamp)
        self.save_character(character, timestamp)