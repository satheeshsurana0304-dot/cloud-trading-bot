import unittest

from src.models import Candle
from src.pattern_engine import (
    candle_body,
    candle_range,
    upper_wick,
    lower_wick,
    is_bullish,
    is_bearish,
)


class TestPatternEngine(unittest.TestCase):

    def setUp(self):
        self.candle = Candle(
            timestamp=1000,
            open=100.0,
            high=110.0,
            low=95.0,
            close=108.0,
            volume=500.0,
        )

    def test_candle_body(self):
        self.assertEqual(candle_body(self.candle), 8.0)

    def test_candle_range(self):
        self.assertEqual(candle_range(self.candle), 15.0)

    def test_upper_wick(self):
        self.assertEqual(upper_wick(self.candle), 2.0)

    def test_lower_wick(self):
        self.assertEqual(lower_wick(self.candle), 5.0)

    def test_bullish_candle(self):
        self.assertTrue(is_bullish(self.candle))
        self.assertFalse(is_bearish(self.candle))


if __name__ == "__main__":
    unittest.main()