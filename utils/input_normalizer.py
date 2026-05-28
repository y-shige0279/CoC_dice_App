import unicodedata


def normalize_input(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)

    minus_chars = {
        "−",  # 数学記号のマイナス
        "－",  # 全角ハイフンマイナス
        "ー",  # 長音記号
        "―",  # 横線
        "–",  # en dash
        "—",  # em dash
    }

    for minus_char in minus_chars:
        normalized = normalized.replace(minus_char, "-")

    return normalized.strip().lower()