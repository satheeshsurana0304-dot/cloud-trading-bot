import csv
from pathlib import Path

from src.models import Candle
from src.patterns import is_knot, is_inverted_knot


DATA_FILE = Path("data/1000PEPE_USDT_1m_1year.csv")

STRONG_BODY_MIN = 0.65


def load_saved_dataset():
    candles = []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            candles.append(
                [
                    int(row["timestamp"]),
                    float(row["open"]),
                    float(row["high"]),
                    float(row["low"]),
                    float(row["close"]),
                    float(row["volume"]),
                ]
            )

    return candles


def diagnose_data_quality(raw_candles):
    timestamps = [candle[0] for candle in raw_candles]

    duplicate_count = 0
    missing_minutes = 0
    backwards_count = 0

    for i in range(1, len(timestamps)):
        difference = timestamps[i] - timestamps[i - 1]

        if difference == 0:
            duplicate_count += 1

        elif difference > 60_000:
            missing_minutes += (difference // 60_000) - 1

        elif difference < 0:
            backwards_count += 1

    print()
    print("=" * 55)
    print("DATA QUALITY")
    print("=" * 55)

    print(f"Total candles:             {len(raw_candles):,}")
    print(f"Duplicate timestamps:      {duplicate_count:,}")
    print(f"Missing 1-minute candles:  {missing_minutes:,}")
    print(f"Backwards timestamps:      {backwards_count:,}")

    if duplicate_count == 0:
        print("Duplicate check:           PASS")
    else:
        print("Duplicate check:           CHECK")

    if missing_minutes == 0:
        print("Continuity check:          PASS")
    else:
        print("Continuity check:          CHECK")

    if backwards_count == 0:
        print("Timestamp order:           PASS")
    else:
        print("Timestamp order:           CHECK")


def diagnose_knot(raw_candles):
    total_windows = len(raw_candles) - 3

    c1_strong = 0
    c2_strong = 0
    c3_bullish = 0
    c3_inside = 0
    c4_bearish = 0
    final_count = 0

    for i in range(total_windows):

        c1 = raw_candles[i]
        c2 = raw_candles[i + 1]
        c3 = raw_candles[i + 2]
        c4 = raw_candles[i + 3]

        c1_range = c1[2] - c1[3]

        if (
            c1_range <= 0
            or c1[4] >= c1[1]
            or (c1[1] - c1[4]) / c1_range < STRONG_BODY_MIN
        ):
            continue

        c1_strong += 1

        c2_range = c2[2] - c2[3]

        if (
            c2_range <= 0
            or c2[4] >= c2[1]
            or (c2[1] - c2[4]) / c2_range < STRONG_BODY_MIN
        ):
            continue

        c2_strong += 1

        if c3[4] <= c3[1]:
            continue

        c3_bullish += 1

        combined_low = min(c1[3], c2[3])
        combined_high = max(c1[2], c2[2])

        if c3[3] < combined_low:
            continue

        if c3[2] > combined_high:
            continue

        c3_inside += 1

        if c4[4] >= c4[1]:
            continue

        c4_bearish += 1

        if c4[4] >= c3[3]:
            continue

        final_count += 1

    print()
    print("=" * 55)
    print("KNOT FILTERING — 65% BODY")
    print("=" * 55)

    print(f"4-candle windows:          {total_windows:,}")
    print(f"C1 strong bearish:         {c1_strong:,}")
    print(f"C1 + C2 strong bearish:   {c2_strong:,}")
    print(f"+ C3 bullish:              {c3_bullish:,}")
    print(f"+ C3 inside range:         {c3_inside:,}")
    print(f"+ C4 bearish:              {c4_bearish:,}")
    print(f"+ C4 closes below C3 low: {final_count:,}")


def diagnose_inverted_knot(raw_candles):
    total_windows = len(raw_candles) - 3

    c1_strong = 0
    c2_strong = 0
    c3_bearish = 0
    c3_inside = 0
    c4_bullish = 0
    final_count = 0

    for i in range(total_windows):

        c1 = raw_candles[i]
        c2 = raw_candles[i + 1]
        c3 = raw_candles[i + 2]
        c4 = raw_candles[i + 3]

        c1_range = c1[2] - c1[3]

        if (
            c1_range <= 0
            or c1[4] <= c1[1]
            or (c1[4] - c1[1]) / c1_range < STRONG_BODY_MIN
        ):
            continue

        c1_strong += 1

        c2_range = c2[2] - c2[3]

        if (
            c2_range <= 0
            or c2[4] <= c2[1]
            or (c2[4] - c2[1]) / c2_range < STRONG_BODY_MIN
        ):
            continue

        c2_strong += 1

        if c3[4] >= c3[1]:
            continue

        c3_bearish += 1

        combined_low = min(c1[3], c2[3])
        combined_high = max(c1[2], c2[2])

        if c3[3] < combined_low:
            continue

        if c3[2] > combined_high:
            continue

        c3_inside += 1

        if c4[4] <= c4[1]:
            continue

        c4_bullish += 1

        if c4[4] <= c3[2]:
            continue

        final_count += 1

    print()
    print("=" * 55)
    print("INVERTED KNOT FILTERING — 65% BODY")
    print("=" * 55)

    print(f"4-candle windows:          {total_windows:,}")
    print(f"C1 strong bullish:         {c1_strong:,}")
    print(f"C1 + C2 strong bullish:   {c2_strong:,}")
    print(f"+ C3 bearish:              {c3_bearish:,}")
    print(f"+ C3 inside range:         {c3_inside:,}")
    print(f"+ C4 bullish:              {c4_bullish:,}")
    print(f"+ C4 closes above C3 high:{final_count:,}")


def verify_pattern_engine(raw_candles):
    candles = [
        Candle(
            timestamp=row[0],
            open=row[1],
            high=row[2],
            low=row[3],
            close=row[4],
            volume=row[5],
        )
        for row in raw_candles
    ]

    knot_count = 0
    inverted_knot_count = 0

    for i in range(len(candles) - 3):

        window = candles[i:i + 4]

        if is_knot(window):
            knot_count += 1

        if is_inverted_knot(window):
            inverted_knot_count += 1

    return knot_count, inverted_knot_count


def main():
    print("1000PEPE/USDT 1-Minute Pattern Diagnostics")
    print("=" * 55)
    print("Strong body threshold: 65%")
    print()

    if not DATA_FILE.exists():
        print("ERROR:")
        print(f"Dataset not found: {DATA_FILE}")
        return

    print("Loading saved dataset...")

    raw_candles = load_saved_dataset()

    print(f"Candles loaded: {len(raw_candles):,}")

    diagnose_data_quality(raw_candles)

    diagnose_knot(raw_candles)

    diagnose_inverted_knot(raw_candles)

    knot_count, inverted_knot_count = verify_pattern_engine(
        raw_candles
    )

    print()
    print("=" * 55)
    print("PATTERN ENGINE VERIFICATION")
    print("=" * 55)

    print(f"KNOT occurrences:          {knot_count:,}")
    print(f"Inverted KNOT occurrences: {inverted_knot_count:,}")

    print()
    print("=" * 55)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 55)


if __name__ == "__main__":
    main()