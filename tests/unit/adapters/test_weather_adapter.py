import unittest
from uuid import uuid4
from api.adapters.weather_adapter import WeatherReportAdapter


class TestWeatherReportAdapter(unittest.TestCase):
    """Test cases for the WeatherReportAdapter."""

    def setUp(self):
        """Set up test data."""
        self.test_id = uuid4()
        # Sample service response for a weather report
        self.service_weather_report = {
            "id": str(self.test_id),
            "city": "London",
            "temperature_current": 22.5,
            "condition": "Sunny",
            "timestamp": "2023-06-15T14:30:00+00:00",
            "temperature_unit": "celsius",
            "humidity": 65.0,
            "location_id": str(uuid4()),
            "source": "API"
        }
        
        # Sample service response for city summaries
        self.service_city_summaries = {
            "cities": [
                {
                    "city": "London",
                    "temperature": 22.5,
                    "condition": "Sunny",
                    "timestamp": "2023-06-15T14:30:00+00:00"
                },
                {
                    "city": "Paris",
                    "temperature": 25.0,
                    "condition": "Cloudy",
                    "timestamp": "2023-06-15T14:00:00Z"
                }
            ]
        }
        
        # Empty service response
        self.empty_service_response = {}

    def test_format_time_with_utc_offset(self):
        """Test formatting a time string with +00:00 UTC offset."""
        time_str = "2023-06-15T14:30:00+00:00"
        result = WeatherReportAdapter.format_time(time_str)
        self.assertEqual(result, "2023-06-15T14:30:00Z")
    
    def test_format_time_with_z(self):
        """Test formatting a time string that already has Z suffix."""
        time_str = "2023-06-15T14:30:00Z"
        result = WeatherReportAdapter.format_time(time_str)
        self.assertEqual(result, time_str)
    
    def test_format_time_none(self):
        """Test formatting None time string."""
        result = WeatherReportAdapter.format_time(None)
        self.assertIsNone(result)
    
    def test_adapt_weather_report(self):
        """Test adapting a weather report from service format to API format."""
        result = WeatherReportAdapter.adapt_weather_report(self.service_weather_report)
        
        self.assertEqual(result["id"], str(self.test_id))
        self.assertEqual(result["city"], "London")
        self.assertEqual(result["temperature"], 22.5)
        self.assertEqual(result["condition"], "Sunny")
        self.assertEqual(result["timestamp"], "2023-06-15T14:30:00Z")
        
    def test_adapt_weather_report_with_temperature_field(self):
        """Test adapting a weather report that uses 'temperature' instead of 'temperature_current'."""
        # Copy the service response and modify it
        service_response = dict(self.service_weather_report)
        service_response["temperature"] = 23.0
        del service_response["temperature_current"]
        
        result = WeatherReportAdapter.adapt_weather_report(service_response)
        
        self.assertEqual(result["temperature"], 23.0)
    
    def test_adapt_weather_report_with_missing_fields(self):
        """Test adapting a weather report with missing fields."""
        result = WeatherReportAdapter.adapt_weather_report(self.empty_service_response)
        
        self.assertIsNone(result["id"])
        self.assertIsNone(result["city"])
        self.assertIsNone(result["temperature"])
        self.assertIsNone(result["condition"])
        self.assertIsNone(result["timestamp"])
    
    def test_adapt_city_summaries(self):
        """Test adapting city summaries from service format to API format."""
        result = WeatherReportAdapter.adapt_city_summaries(self.service_city_summaries)
        
        self.assertIn("cities", result)
        self.assertEqual(len(result["cities"]), 2)
        
        # Check first city
        london = result["cities"][0]
        self.assertEqual(london["city"], "London")
        self.assertEqual(london["temperature"], 22.5)
        self.assertEqual(london["condition"], "Sunny")
        self.assertEqual(london["timestamp"], "2023-06-15T14:30:00Z")
        
        # Check second city
        paris = result["cities"][1]
        self.assertEqual(paris["city"], "Paris")
        self.assertEqual(paris["temperature"], 25.0)
        self.assertEqual(paris["condition"], "Cloudy")
        self.assertEqual(paris["timestamp"], "2023-06-15T14:00:00Z")
    
    def test_adapt_city_summaries_with_empty_response(self):
        """Test adapting city summaries from an empty service response."""
        result = WeatherReportAdapter.adapt_city_summaries(self.empty_service_response)
        
        self.assertIn("cities", result)
        self.assertEqual(len(result["cities"]), 0)
    
    def test_adapt_city_summaries_with_none_response(self):
        """Test adapting city summaries from a None service response."""
        result = WeatherReportAdapter.adapt_city_summaries(None)
        
        self.assertIn("cities", result)
        self.assertEqual(len(result["cities"]), 0)


if __name__ == "__main__":
    unittest.main() 