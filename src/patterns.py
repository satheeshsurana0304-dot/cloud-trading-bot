from src.models import Candle


STRONG_BODY_MIN = 0.65
MOMENTUM_BODY_MIN = 0.80


def _is_strong_bearish(candle: Candle) -> bool:
    candle_range = candle.high - candle.low

    if candle_range <= 0:
        return False

    body = candle.open - candle.close

    return (
        candle.close < candle.open
        and body / candle_range >= STRONG_BODY_MIN
    )


def _is_strong_bullish(candle: Candle) -> bool:
    candle_range = candle.high - candle.low

    if candle_range <= 0:
        return False

    body = candle.close - candle.open

    return (
        candle.close > candle.open
        and body / candle_range >= STRONG_BODY_MIN
    )


def _is_bullish(candle: Candle) -> bool:
    return candle.close > candle.open


def _is_bearish(candle: Candle) -> bool:
    return candle.close < candle.open


def _body_percentage(candle: Candle) -> float:
    candle_range = candle.high - candle.low

    if candle_range <= 0:
        return 0.0

    body = abs(candle.close - candle.open)

    return body / candle_range


def is_knot(candles: list[Candle]) -> bool:
    """
    KNOT pattern.

    C1 = strong bearish candle, body >= 65%
    C2 = strong bearish candle, body >= 65%
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
    Inverted KNOT pattern.

    C1 = strong bullish candle, body >= 65%
    C2 = strong bullish candle, body >= 65%
    C3 = bearish candle inside combined C1-C2 range
    C4 = bullish candle closing above C3 high
    """

    if len(candles) != 4:
        return False

    c1, c2, c3, c4 = candles

    if not _is_strong_bullish(c1):
        return False

    if not _is_strong_bullish(c2):
        return False

    if not _is_bearish(c3):
        return False

    combined_low = min(c1.low, c2.low)
    combined_high = max(c1.high, c2.high)

    if c3.low < combined_low:
        return False

    if c3.high > combined_high:
        return False

    if not _is_bullish(c4):
        return False

    if c4.close <= c3.high:
        return False

    return True


def is_three_candle_momentum(candles: list[Candle]) -> bool:
    """
    3-Candle Momentum pattern.

    Three consecutive candles must:
        1. Be the same direction.
        2. Each have a body >= 80% of its total range.

    Valid structures:

        Bullish:
            C1 bullish >= 80%
            C2 bullish >= 80%
            C3 bullish >= 80%

        Bearish:
            C1 bearish >= 80%
            C2 bearish >= 80%
            C3 bearish >= 80%
    """

    if len(candles) != 3:
        return False

    c1, c2, c3 = candles

    if (
        _body_percentage(c1) < MOMENTUM_BODY_MIN
        or _body_percentage(c2) < MOMENTUM_BODY_MIN
        or _body_percentage(c3) < MOMENTUM_BODY_MIN
    ):
        return False

    bullish = (
        _is_bullish(c1)
        and _is_bullish(c2)
        and _is_bullish(c3)
    )

    bearish = (
        _is_bearish(c1)
        and _is_bearish(c2)
        and _is_bearish(c3)
    )

    return bullish or bearish


# ============================================================
# PATTERN LIBRARY
# ============================================================

PATTERN_LIBRARY = {
    "KNOT": is_knot,
    "INVERTED_KNOT": is_inverted_knot,
    "THREE_CANDLE_MOMENTUM": is_three_candle_momentum,
}