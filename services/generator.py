# services/generator.py
import logging
from models.character import Character
from models.config import Edition, BonusType, DiceRule, MAX_REROLLS
from models.logger import RollLogger
from models.status import StatusName, StatusResult, StatusValue
from services.checker import check_conditions
from utils.dice import roll_dice

# 能力値の生成関数
def generate_status(editions: Edition,status_config: dict[str, dict[str, DiceRule]]) -> StatusResult:
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
def generate_character(
    editions: Edition,
    status_config: dict[str, dict[str, DiceRule]],
    target_total: dict[str, int],
    target_status: dict[str, dict[str, list[int]]],
    bonus_inputs: list[tuple[StatusName, BonusType, int, str]],) -> Character:
    reroll_cnt = 0
    logger = RollLogger(edition=editions)
    
    while True:
        # 能力値を生成
        result = generate_status(editions, status_config)
        
        character = Character(
            logger=logger,
            status=result,
            edition=editions,
            reroll_cnt=reroll_cnt,
        )

        for status_name, history_type, value, reason in bonus_inputs:
            character.apply_bonus(
                status_name,
                history_type=history_type,
                value=value,
                reason=reason,
            )
    
        # ログに生成結果を追加
        logger.add_roll(character.status)
        
        if check_conditions(character.status, editions, target_total, target_status):
            break
        reroll_cnt += 1
        
        if reroll_cnt % 100 == 0:
            logging.debug(f"Reroll count: {reroll_cnt}")
        
        if reroll_cnt >= MAX_REROLLS:
            logging.info("Maximum number of rerolls reached. Exiting.")
            break
    
    character.reroll_cnt = reroll_cnt
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