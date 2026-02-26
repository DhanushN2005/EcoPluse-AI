import unittest
from ecopulse_ai.streaming.pathway_pipeline import calculate_analytics

class TestEnvironmentalAnalytics(unittest.TestCase):
    def setUp(self):
        self.sample_record = {
            'aqi': 50,
            'co2': 400,
            'pm25': 12,
            'traffic_density': 30,
            'industrial_index': 20,
            'wind_speed': 10,
            'temperature': 25,
            'humidity': 50
        }

    def test_health_score_calculation(self):
        """Test that health score decreases as pollutants increase."""
        record = calculate_analytics(self.sample_record.copy())
        base_score = record['health_score']
        
        # Increase AQI
        bad_record = self.sample_record.copy()
        bad_record['aqi'] = 300
        result = calculate_analytics(bad_record)
        
        self.assertLess(result['health_score'], base_score)

    def test_severity_levels(self):
        """Test that severity levels are correctly assigned."""
        record = self.sample_record.copy()
        record['aqi'] = 350
        result = calculate_analytics(record)
        self.assertEqual(result['severity'], "Emergency")

if __name__ == '__main__':
    unittest.main()
