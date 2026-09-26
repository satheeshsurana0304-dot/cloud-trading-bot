import unittest
from pathlib import Path

from src.data_store import save_candles
from src.models import Candle


class TestDataStore(unittest.TestCase):

    def test_save_candles(self):
        candles = [
            Candle(1000, 100.0, 105.0, 95.0, 103.0, 500.0),
            Candle(2000, 103.0, 108.0, 101.0, 107.0, 600.0),
        ]

        file_path = save_candles(candles, "test_candles.csv")

        self.assertTrue(file_path.exists())

        content = file_path.read_text(encoding="utf-8")

        self.assertIn("timestamp,open,high,low,close,volume", content)
        self.assertIn("1000,100.0,105.0,95.0,103.0,500.0", content)
        self.assertIn("2000,103.0,108.0,101.0,107.0,600.0", content)

        file_path.unlink()


if __name__ == "__main__":
    unittest.main()