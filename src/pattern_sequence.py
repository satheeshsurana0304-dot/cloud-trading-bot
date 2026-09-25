from src.models import Candle


def validate_sequence(candles: list[Candle]) -> bool:
    return len(candles) > 0


def sequence_length(candles: list[Candle]) -> int:
    return len(candles)