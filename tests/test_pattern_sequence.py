import unittest

from src.models import Candle
from src.pattern_sequence import validate_sequence, sequence_length


class TestPatternSequence(unittest.TestCase):

    def setUp(self):
        self.candles = [
            Candle(1, 100, 105, 95, 103, 500),
            Candle(2, 103, 108, 101, 107, 600),
            Candle(3, 107, 110, 104, 109, 700),
        ]

    def test_valid_sequence(self):
        self.assertTrue(validate_sequence(self.candles))

    def test_empty_sequence(self):
        self.assertFalse(validate_sequence([]))

    def test_sequence_length(self):
        self.assertEqual(sequence_length(self.candles), 3)


if __name__ == "__main__":
    unittest.main()
    