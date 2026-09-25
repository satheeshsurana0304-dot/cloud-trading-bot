from src.models import Candle


def candle_body(candle: Candle) -> float:
    return abs(candle.close - candle.open)


def candle_range(candle: Candle) -> float:
    return candle.high - candle.low


def upper_wick(candle: Candle) -> float:
    return candle.high - max(candle.open, candle.close)


def lower_wick(candle: Candle) -> float:
    return min(candle.open, candle.close) - candle.low


def is_bullish(candle: Candle) -> bool:
    return candle.close > candle.open


def is_bearish(candle: Candle) -> bool:
    return candle.close < candle.open
