import time
from pathlib import Path

import ccxt

from src.models import Candle
from src.patterns import is_knot, is_inverted_knot


SYMBOL = "BTC/USDT"
TIMEFRAME = "1m"

TOTAL_CANDLES = 100_000
BATCH_SIZE = 1000

DATA_FILE = Path("data/BTC_USDT_1m_100000.csv")


def download_large_dataset():
    exchange = ccxt.binanceusdm()

    timeframe_ms = 60_000
    now = int(time.time() * 1000)

    since = now - (TOTAL_CANDLES * timeframe_ms)

    candles = []

    while len(candles) < TOTAL_CANDLES:
        remaining = TOTAL_CANDLES - len(candles)
        limit = min(BATCH_SIZE, remaining)

        batch = exchange.fetch_ohlcv(
            SYMBOL,
            TIMEFRAME,
            since=since,
            limit=limit,
        )

        if not batch:
            break

        candles.extend(batch)

        since = batch[-1][0] + timeframe_ms

        print(f"Downloaded: {len(candles)}/{TOTAL_CANDLES}")

        time.sleep(0.1)

    candles = candles[:TOTAL_CANDLES]

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with DATA_FILE.open("w", encoding="utf-8") as file:
        file.write("timestamp,open,high,low,close,volume\n")

        for candle in candles:
            file.write(
                f"{candle[0]},"
                f"{candle[1]},"
                f"{candle[2]},"
                f"{candle[3]},"
                f"{candle[4]},"
                f"{candle[5]}\n"
            )

    print()
    print(f"Saved dataset to: {DATA_FILE}")

    return candles


def load_saved_dataset():
    candles = []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        next(file)  # Skip header

        for line in file:
            values = line.strip().split(",")

            candles.append([
                int(values[0]),
                float(values[1]),
                float(values[2]),
                float(values[3]),
                float(values[4]),
                float(values[5]),
            ])

    return candles


def get_dataset():
    if DATA_FILE.exists():
        print(f"Found saved dataset:")
        print(DATA_FILE)
        print("Loading local candles...")
        print()

        return load_saved_dataset()

    print("Saved dataset not found.")
    print("Downloading 100,000 candles from Binance...")
    print()

    return download_large_dataset()


def scan_patterns(raw_candles):
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

    knot_matches = []
    inverted_knot_matches = []

    for i in range(len(candles) - 3):
        window = candles[i:i + 4]

        if is_knot(window):
            knot_matches.append((i, window))

        if is_inverted_knot(window):
            inverted_knot_matches.append((i, window))

    return knot_matches, inverted_knot_matches


def main():
    print("BTC/USDT 1-minute pattern scanner")
    print("=" * 45)
    print()

    raw_candles = get_dataset()

    print(f"Candles loaded: {len(raw_candles):,}")

    print()
    print("Scanning for KNOT and Inverted KNOT...")

    knot_matches, inverted_knot_matches = scan_patterns(raw_candles)

    print()
    print("=" * 45)
    print(f"Candles scanned:       {len(raw_candles):,}")
    print(f"KNOT occurrences:      {len(knot_matches):,}")
    print(f"Inverted KNOT:         {len(inverted_knot_matches):,}")
    print("=" * 45)

    if knot_matches:
        print()
        print("First 10 KNOT occurrences:")

        for number, (index, window) in enumerate(
            knot_matches[:10],
            start=1,
        ):
            print(
                f"KNOT #{number}: "
                f"index={index}, "
                f"timestamp={window[0].timestamp}"
            )

    if inverted_knot_matches:
        print()
        print("First 10 Inverted KNOT occurrences:")

        for number, (index, window) in enumerate(
            inverted_knot_matches[:10],
            start=1,
        ):
            print(
                f"Inverted KNOT #{number}: "
                f"index={index}, "
                f"timestamp={window[0].timestamp}"
            )


if __name__ == "__main__":
    main()