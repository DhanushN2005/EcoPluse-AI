import unittest
from ecopulse_ai.analytics.alerts import get_alert_status

class TestAlertSystem(unittest.TestCase):
    def test_no_alerts(self):
        """No alerts should trigger for safe values."""
        data = {'aqi': 40, 'co2': 380}
        alerts = get_alert_status(data)
        self.assertEqual(len(alerts), 0)

    def test_emergency_aqi(self):
        """Emergency alert should trigger for high AQI."""
        data = {'aqi': 350, 'co2': 400}
        alerts = get_alert_status(data)
        self.assertTrue(any(a['level'] == 'Emergency' for a in alerts))

    def test_co2_warning(self):
        """Warning alert should trigger for high CO2."""
        data = {'aqi': 50, 'co2': 1100}
        alerts = get_alert_status(data)
        self.assertTrue(any(a['type'] == 'CO2' and a['level'] == 'Warning' for a in alerts))

if __name__ == '__main__':
    unittest.main()
