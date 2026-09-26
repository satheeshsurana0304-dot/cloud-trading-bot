import ccxt

from src.models import Candle


def create_exchange():
    return ccxt.binanceusdm()


def convert_candle(raw_candle):
    return Candle(
        timestamp=raw_candle[0],
        open=raw_candle[1],
        high=raw_candle[2],
        low=raw_candle[3],
        close=raw_candle[4],
        volume=raw_candle[5],
    )


def fetch_candles(
    symbol: str,
    timeframe: str = "1m",
    limit: int = 10,
    since: int | None = None,
):
    exchange = create_exchange()

    raw_candles = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        since=since,
        limit=limit,
    )

    return [convert_candle(candle) for candle in raw_candles]