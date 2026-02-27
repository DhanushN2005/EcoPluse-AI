"""
Unit tests for the EcoPulse AI Streaming Analytics engine.
This suite validates telemetry processing, health indexing, and risk severity assignment.
"""

import unittest
from ecopulse_ai.streaming.pathway_pipeline import calculate_analytics


class TestEnvironmentalAnalytics(unittest.TestCase):
    """
    Test suite for validating environmental data transformations and analytics logic.
    """

    def setUp(self) -> None:
        """Initialize standard baseline telemetry for testing."""
        self.sample_record = {
            "aqi": 50.0,
            "co2": 400.0,
            "pm25": 12.0,
            "traffic_density": 30.0,
            "industrial_index": 20.0,
            "wind_speed": 10.0,
            "temperature": 25.0,
            "humidity": 50.0,
        }

    def test_health_score_calculation(self) -> None:
        """
        Verify that the health index correctly reflects deteriorating environmental conditions.
        Increases in pollutants should lead to a measurable decrease in the composite health score.
        """
        record = calculate_analytics(self.sample_record.copy())
        base_score = record["health_score"]

        # Simulate a significant pollution spike
        bad_record = self.sample_record.copy()
        bad_record["aqi"] = 300.0
        result = calculate_analytics(bad_record)

        self.assertLess(
            result["health_score"], base_score, "Health score did not decrease during AQI spike."
        )

    def test_severity_levels(self) -> None:
        """
        Validate the multi-tier risk classification engine.
        Ensures that high AQI values trigger the appropriate 'Emergency' response status.
        """
        record = self.sample_record.copy()
        record["aqi"] = 350.0
        result = calculate_analytics(record)
        self.assertEqual(
            result["severity"], "Emergency", "Failed to classify hazardous AQI as 'Emergency'."
        )


if __name__ == "__main__":
    unittest.main()
