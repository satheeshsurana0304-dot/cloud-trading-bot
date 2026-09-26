import unittest

from src import config


class TestConfig(unittest.TestCase):

    def test_basic_configuration(self):
        self.assertEqual(config.APP_NAME, "cloud-trading-bot")
        self.assertEqual(config.ENVIRONMENT, "development")
        self.assertEqual(config.EXCHANGE, "binance")
        self.assertEqual(config.MARKET_TYPE, "futures")

    def test_market_defaults(self):
        self.assertEqual(config.DEFAULT_SYMBOL, "BTC/USDT")
        self.assertEqual(config.DEFAULT_TIMEFRAME, "1m")
        self.assertEqual(config.HISTORICAL_CANDLE_LIMIT, 1000)


if __name__ == "__main__":
    unittest.main()