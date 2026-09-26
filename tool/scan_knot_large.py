import time
import ccxt

from src.models import Candle
from src.patterns import is_knot


SYMBOL = "BTC/USDT"
TIMEFRAME = "1m"
TOTAL_CANDLES = 100_000
BATCH_SIZE = 1000


def fetch_large_dataset():
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

        print(
            f"Downloaded: {len(candles)}/{TOTAL_CANDLES}"
        )

        time.sleep(0.1)

    return candles[:TOTAL_CANDLES]


def scan_knot(raw_candles):
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

    matches = []

    for i in range(len(candles) - 3):
        window = candles[i:i + 4]

        if is_knot(window):
            matches.append((i, window))

    return matches


def main():
    print("Downloading BTC/USDT 1-minute data...")
    print(f"Target candles: {TOTAL_CANDLES:,}")
    print()

    raw_candles = fetch_large_dataset()

    print()
    print(f"Candles downloaded: {len(raw_candles):,}")

    print()
    print("Scanning for KNOT...")

    matches = scan_knot(raw_candles)

    print()
    print("=" * 40)
    print(f"Candles scanned:   {len(raw_candles):,}")
    print(f"KNOT occurrences:  {len(matches):,}")
    print("=" * 40)

    if matches:
        print()
        print("First 10 KNOT occurrences:")

        for number, (index, window) in enumerate(matches[:10], start=1):
            print(
                f"KNOT #{number}: "
                f"index={index}, "
                f"timestamp={window[0].timestamp}"
            )


if __name__ == "__main__":
    main()