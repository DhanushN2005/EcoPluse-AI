import unittest
from ecopulse_ai.analytics.health_score import calculate_composite_health


class TestHealthScore(unittest.TestCase):
    def test_perfect_scenario(self):
        """Test score with baseline safe values."""
        score = calculate_composite_health(40, 350, 10, 50)
        self.assertEqual(score, 100.0)

    def test_extreme_pollution(self):
        """Test score with hazardous values."""
        score = calculate_composite_health(400, 1500, 120, 50)
        self.assertEqual(score, 0.0)

    def test_partial_degradation(self):
        """Test middle-ground values."""
        # AQI 100 (penalty 50/300 * 40 = 6.6)
        # CO2 800 (penalty 400/1000 * 30 = 12)
        # PM25 45 (penalty 30/100 * 30 = 9)
        # Expected: 100 - (6.7 + 12 + 9) approx 72.3
        score = calculate_composite_health(100, 800, 45, 50)
        self.assertTrue(70 <= score <= 75)


if __name__ == "__main__":
    unittest.main()
