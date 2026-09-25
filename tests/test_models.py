import unittest

from src.models import Candle


class TestCandle(unittest.TestCase):

    def test_candle_creation(self):
        candle = Candle(
            timestamp=1000,
            open=100.0,
            high=105.0,
            low=95.0,
            close=103.0,
            volume=500.0,
        )

        self.assertEqual(candle.open, 100.0)
        self.assertEqual(candle.high, 105.0)
        self.assertEqual(candle.low, 95.0)
        self.assertEqual(candle.close, 103.0)
        self.assertEqual(candle.volume, 500.0)


if __name__ == "__main__":
    unittest.main()