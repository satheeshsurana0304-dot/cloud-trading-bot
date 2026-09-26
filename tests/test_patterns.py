import unittest

from src.models import Candle
from src.patterns import is_knot


class TestKnot(unittest.TestCase):

    def test_valid_knot(self):
        candles = [
            Candle(1, 110, 111, 99, 100, 500),
            Candle(2, 100, 101, 90, 91, 600),
            Candle(3, 95, 98, 92, 97, 400),
            Candle(4, 97, 98, 85, 89, 700),
        ]

        self.assertTrue(is_knot(candles))

    def test_wrong_number_of_candles(self):
        candles = [
            Candle(1, 110, 111, 99, 100, 500),
            Candle(2, 100, 101, 90, 91, 600),
            Candle(3, 95, 98, 92, 97, 400),
        ]

        self.assertFalse(is_knot(candles))

    def test_weak_first_candle(self):
        candles = [
            Candle(1, 110, 115, 95, 105, 500),
            Candle(2, 100, 101, 90, 91, 600),
            Candle(3, 95, 98, 92, 97, 400),
            Candle(4, 97, 98, 85, 89, 700),
        ]

        self.assertFalse(is_knot(candles))

    def test_c3_outside_range(self):
        candles = [
            Candle(1, 110, 111, 99, 100, 500),
            Candle(2, 100, 101, 90, 91, 600),
            Candle(3, 95, 115, 92, 104, 400),
            Candle(4, 104, 105, 85, 89, 700),
        ]

        self.assertFalse(is_knot(candles))

    def test_c4_does_not_close_below_c3_low(self):
        candles = [
            Candle(1, 110, 111, 99, 100, 500),
            Candle(2, 100, 101, 90, 91, 600),
            Candle(3, 95, 98, 92, 97, 400),
            Candle(4, 97, 98, 91, 93, 700),
        ]

        self.assertFalse(is_knot(candles))


if __name__ == "__main__":
    unittest.main()