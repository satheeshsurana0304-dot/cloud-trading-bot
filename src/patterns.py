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


def _is_strong_bullish(candle: Candle) -> bool:
    candle_range = candle.high - candle.low

    if candle_range <= 0:
        return False

    body = candle.close - candle.open

    return (
        candle.close > candle.open
        and body / candle_range >= 0.80
    )


def _is_bullish(candle: Candle) -> bool:
    return candle.close > candle.open


def _is_bearish(candle: Candle) -> bool:
    return candle.close < candle.open


def is_knot(candles: list[Candle]) -> bool:
    """
    Detect the base KNOT pattern.

    Structure:
        C1 = strong bearish candle
        C2 = strong bearish candle
        C3 = bullish candle inside combined C1-C2 range
        C4 = bearish candle closing below C3 low
    """

    if len(candles) != 4:
        return False

    c1, c2, c3, c4 = candles

    if not _is_strong_bearish(c1):
        return False

    if not _is_strong_bearish(c2):
        return False

    if not _is_bullish(c3):
        return False

    combined_low = min(c1.low, c2.low)
    combined_high = max(c1.high, c2.high)

    if c3.low < combined_low:
        return False

    if c3.high > combined_high:
        return False

    if not _is_bearish(c4):
        return False

    if c4.close >= c3.low:
        return False

    return True


def is_inverted_knot(candles: list[Candle]) -> bool:
    """
    Detect the inverted KNOT pattern.

    Structure:
        C1 = strong bullish candle
        C2 = strong bullish candle
        C3 = bearish candle inside combined C1-C2 range
        C4 = bullish candle closing above C3 high
    """

    if len(candles) != 4:
        return False

    c1, c2, c3, c4 = candles

    # C1 and C2 must be strong bullish candles.
    if not _is_strong_bullish(c1):
        return False

    if not _is_strong_bullish(c2):
        return False

    # C3 must be bearish.
    if not _is_bearish(c3):
        return False

    # C3 must be completely inside the combined
    # price range of C1 and C2.
    combined_low = min(c1.low, c2.low)
    combined_high = max(c1.high, c2.high)

    if c3.low < combined_low:
        return False

    if c3.high > combined_high:
        return False

    # C4 must be bullish.
    if not _is_bullish(c4):
        return False

    # C4 must close above C3 high.
    if c4.close <= c3.high:
        return False

    return True