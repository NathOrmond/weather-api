import unittest
from datetime import datetime
from uuid import UUID, uuid4

from api.schemas import (
    WeatherReportCreateSchema, 
    WeatherReportSchema,
    CityWeatherSummarySchema,
    WeatherSummarySchema
)


class TestWeatherSchemas(unittest.TestCase):
    """Test cases for the weather-related schemas."""

    def setUp(self):
        """Set up test data."""
        self.test_id = uuid4()
        self.valid_create_data = {
            "city": "London",
            "temperature": 22.5,
            "condition": "Sunny",
            "timestamp": "2023-06-15T14:30:00Z",
            "humidity": 65.0
        }
        
        self.valid_report_data = {
            "id": str(self.test_id),
            "city": "London",
            "temperature": 22.5,
            "condition": "Sunny",
            "timestamp": "2023-06-15T14:30:00Z"
        }
        
        self.valid_summary_item = {
            "city": "London",
            "temperature": 22.5,
            "condition": "Sunny",
            "timestamp": "2023-06-15T14:30:00Z"
        }
        
        self.valid_summary_data = {
            "cities": [
                self.valid_summary_item,
                {
                    "city": "Paris",
                    "temperature": 25.0,
                    "condition": "Cloudy",
                    "timestamp": "2023-06-15T14:00:00Z"
                }
            ]
        }

    def test_weather_report_create_schema_valid(self):
        """Test WeatherReportCreateSchema with valid data."""
        schema = WeatherReportCreateSchema()
        result = schema.load(self.valid_create_data)
        
        self.assertEqual(result["city"], "London")
        self.assertEqual(result["temperature"], 22.5)
        self.assertEqual(result["condition"], "Sunny")
        self.assertIsInstance(result["timestamp"], datetime)
        self.assertEqual(result["humidity"], 65.0)
    
    def test_weather_report_create_schema_minimal(self):
        """Test WeatherReportCreateSchema with minimal valid data (without optional fields)."""
        schema = WeatherReportCreateSchema()
        minimal_data = {
            "city": "London",
            "temperature": 22.5,
            "condition": "Sunny"
        }
        
        result = schema.load(minimal_data)
        
        self.assertEqual(result["city"], "London")
        self.assertEqual(result["temperature"], 22.5)
        self.assertEqual(result["condition"], "Sunny")
        self.assertNotIn("timestamp", result)
        self.assertNotIn("humidity", result)
    
    def test_weather_report_create_schema_invalid_condition(self):
        """Test WeatherReportCreateSchema with invalid condition value."""
        schema = WeatherReportCreateSchema()
        invalid_data = self.valid_create_data.copy()
        invalid_data["condition"] = "Invalid"
        
        with self.assertRaises(Exception) as context:
            schema.load(invalid_data)
        
        self.assertIn("condition", str(context.exception))
    
    def test_weather_report_create_schema_invalid_humidity(self):
        """Test WeatherReportCreateSchema with humidity outside valid range."""
        schema = WeatherReportCreateSchema()
        invalid_data = self.valid_create_data.copy()
        invalid_data["humidity"] = 101.0  # Over 100%
        
        with self.assertRaises(Exception) as context:
            schema.load(invalid_data)
        
        self.assertIn("humidity", str(context.exception))
    
    def test_weather_report_schema_valid(self):
        """Test WeatherReportSchema with valid data."""
        schema = WeatherReportSchema()
        result = schema.load(self.valid_report_data)
        
        # Compare string representations of UUIDs
        self.assertEqual(str(result["id"]), str(self.test_id))
        self.assertEqual(result["city"], "London")
        self.assertEqual(result["temperature"], 22.5)
        self.assertEqual(result["condition"], "Sunny")
        # Check timestamp as string
        self.assertEqual(result["timestamp"], "2023-06-15T14:30:00Z")
    
    def test_weather_report_schema_dump(self):
        """Test WeatherReportSchema serialization."""
        schema = WeatherReportSchema()
        
        # Directly dump the data since we're using strings now
        serialized = schema.dump(self.valid_report_data)
        
        self.assertEqual(serialized["id"], str(self.test_id))
        self.assertEqual(serialized["city"], "London")
        self.assertEqual(serialized["temperature"], 22.5)
        self.assertEqual(serialized["condition"], "Sunny")
        self.assertEqual(serialized["timestamp"], "2023-06-15T14:30:00Z")
    
    def test_city_weather_summary_schema(self):
        """Test CityWeatherSummarySchema with valid data."""
        schema = CityWeatherSummarySchema()
        result = schema.load(self.valid_summary_item)
        
        self.assertEqual(result["city"], "London")
        self.assertEqual(result["temperature"], 22.5)
        self.assertEqual(result["condition"], "Sunny")
        # Check timestamp as string
        self.assertEqual(result["timestamp"], "2023-06-15T14:30:00Z")
    
    def test_weather_summary_schema(self):
        """Test WeatherSummarySchema with valid data."""
        schema = WeatherSummarySchema()
        result = schema.load(self.valid_summary_data)
        
        self.assertIn("cities", result)
        self.assertEqual(len(result["cities"]), 2)
        
        london = result["cities"][0]
        self.assertEqual(london["city"], "London")
        self.assertEqual(london["temperature"], 22.5)
        self.assertEqual(london["condition"], "Sunny")
        # Check timestamp as string
        self.assertEqual(london["timestamp"], "2023-06-15T14:30:00Z")
    
    def test_weather_summary_schema_ensure_structure(self):
        """Test WeatherSummarySchema's ensure_structure method with different inputs."""
        schema = WeatherSummarySchema()
        
        # Create an object with missing cities key and test that post_dump 
        # would transform it to have an empty cities list
        result = {"other_key": "value"}
        processed = schema.ensure_structure(result)
        self.assertIn("cities", processed)
        self.assertEqual(len(processed["cities"]), 0)
        
        # Test with None
        result = schema.ensure_structure(None)
        self.assertIn("cities", result)
        self.assertEqual(len(result["cities"]), 0)


if __name__ == "__main__":
    unittest.main() 