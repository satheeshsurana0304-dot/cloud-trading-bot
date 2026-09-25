import unittest

from src.market_data import convert_candle


class TestMarketData(unittest.TestCase):

    def test_convert_candle(self):
        raw_candle = [
            1000,
            100.0,
            105.0,
            95.0,
            103.0,
            500.0,
        ]

        candle = convert_candle(raw_candle)

        self.assertEqual(candle.timestamp, 1000)
        self.assertEqual(candle.open, 100.0)
        self.assertEqual(candle.high, 105.0)
        self.assertEqual(candle.low, 95.0)
        self.assertEqual(candle.close, 103.0)
        self.assertEqual(candle.volume, 500.0)


if __name__ == "__main__":
    unittest.main()
    