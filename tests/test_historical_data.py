import unittest
from pathlib import Path
from unittest.mock import patch

from src.historical_data import download_historical_candles
from src.models import Candle


class TestHistoricalData(unittest.TestCase):

    @patch("src.historical_data.save_candles")
    @patch("src.historical_data.fetch_candles")
    def test_download_historical_candles(
        self,
        mock_fetch_candles,
        mock_save_candles,
    ):
        candles = [
            Candle(1000, 100.0, 105.0, 95.0, 103.0, 500.0),
        ]

        mock_fetch_candles.return_value = candles
        mock_save_candles.return_value = Path("data/test.csv")

        result = download_historical_candles(
            symbol="BTC/USDT",
            timeframe="1m",
            limit=1000,
            filename="test.csv",
        )

        mock_fetch_candles.assert_called_once_with(
            symbol="BTC/USDT",
            timeframe="1m",
            limit=1000,
        )

        mock_save_candles.assert_called_once_with(
            candles,
            "test.csv",
        )

        self.assertEqual(result, Path("data/test.csv"))


if __name__ == "__main__":
    unittest.main()