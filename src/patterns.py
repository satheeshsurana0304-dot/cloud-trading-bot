from src.models import Candle


def _is_strong_bearish(candle: Candle) -> bool:
    candle_range = candle.high - candle.low

    if candle_range <= 0:
        return False

    body = candle.open - candle.close

    return (
        candle.close < candle.open
        and body / candle_range >= 0.80
    )


def _is_bullish(candle: Candle) -> bool:
    return candle.close > candle.open


def is_knot(candles: list[Candle]) -> bool:
    """
    Detect the base KNOT pattern.

    Structure:
        C1 = strong bearish candle
        C2 = strong bearish candle
        C3 = bullish candle inside the combined C1-C2 range
        C4 = bearish candle closing below C3 low
    """

    if len(candles) != 4:
        return False

    c1, c2, c3, c4 = candles

    # C1 and C2 must be strong bearish candles.
    if not _is_strong_bearish(c1):
        return False

    if not _is_strong_bearish(c2):
        return False

    # C3 must be bullish.
    if not _is_bullish(c3):
        return False

    # C3 must be completely inside the combined
    # price range of C1 and C2.
    combined_low = min(c1.low, c2.low)
    combined_high = max(c1.high, c2.high)

    if c3.low < combined_low:
        return False

    if c3.high > combined_high:
        return False

    # C4 must be bearish.
    if c4.close >= c4.open:
        return False

    # C4 must close below C3 low.
    if c4.close >= c3.low:
        return False

    return True