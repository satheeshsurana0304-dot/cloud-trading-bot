import csv
from pathlib import Path

from src.models import Candle


DATA_DIRECTORY = Path("data")


def save_candles(candles: list[Candle], filename: str) -> Path:
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

    file_path = DATA_DIRECTORY / filename

    with file_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ])

        for candle in candles:
            writer.writerow([
                candle.timestamp,
                candle.open,
                candle.high,
                candle.low,
                candle.close,
                candle.volume,
            ])

    return file_path