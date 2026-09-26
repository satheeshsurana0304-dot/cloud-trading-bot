import unittest
from pathlib import Path
from unittest.mock import patch

from src.historical_data import download_historical_candles
from src.models import Candle


class TestHistoricalPagination(unittest.TestCase):

    @patch("src.historical_data.MAX_BATCH_SIZE", 2)
    @patch("src.historical_data.save_candles")
    @patch("src.historical_data.fetch_candles")
    def test_multiple_batches(
        self,
        mock_fetch_candles,
        mock_save_candles,
    ):
        batch_1 = [
            Candle(1000, 100, 105, 95, 103, 500),
            Candle(2000, 103, 108, 101, 107, 600),
        ]

        batch_2 = [
            Candle(3000, 107, 110, 104, 109, 700),
            Candle(4000, 109, 112, 108, 111, 800),
        ]

        mock_fetch_candles.side_effect = [
            batch_1,
            batch_2,
        ]

        mock_save_candles.return_value = Path(
            "data/test_pagination.csv"
        )

        result = download_historical_candles(
            symbol="BTC/USDT",
            timeframe="1m",
            total_candles=4,
            filename="test_pagination.csv",
        )

        self.assertEqual(mock_fetch_candles.call_count, 2)

        mock_fetch_candles.assert_any_call(
            symbol="BTC/USDT",
            timeframe="1m",
            limit=2,
        )

        mock_fetch_candles.assert_any_call(
            symbol="BTC/USDT",
            timeframe="1m",
            limit=2,
            since=2001,
        )

        mock_save_candles.assert_called_once_with(
            batch_1 + batch_2,
            "test_pagination.csv",
        )

        self.assertEqual(
            result,
            Path("data/test_pagination.csv"),
        )


if __name__ == "__main__":
    unittest.main()