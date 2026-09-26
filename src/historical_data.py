from src.data_store import save_candles
from src.market_data import fetch_candles


MAX_BATCH_SIZE = 1000


def download_historical_candles(
    symbol: str,
    timeframe: str = "1m",
    total_candles: int = 1000,
    filename: str = "historical_candles.csv",
    since: int | None = None,
    limit: int | None = None,
):
    if limit is not None:
        total_candles = limit

    all_candles = []

    remaining = total_candles
    current_since = since

    while remaining > 0:
        batch_size = min(remaining, MAX_BATCH_SIZE)

        if current_since is None:
            candles = fetch_candles(
                symbol=symbol,
                timeframe=timeframe,
                limit=batch_size,
            )
        else:
            candles = fetch_candles(
                symbol=symbol,
                timeframe=timeframe,
                limit=batch_size,
                since=current_since,
            )

        if not candles:
            break

        all_candles.extend(candles)
        remaining -= len(candles)

        if len(candles) < batch_size:
            break

        current_since = candles[-1].timestamp + 1

    return save_candles(all_candles, filename)