import unittest
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime, timezone

from api.controllers.weather_controller import (
    add_weather_report, get_all_city_summaries, 
    get_city_weather, update_city_weather, delete_city_weather
)
from api.models.domain import (
    City, Location, Report, Condition, ReportCondition,
    ConditionType, IntensityLevel, TemperatureUnit
)


class TestWeatherController(unittest.TestCase):
    """Test cases for the weather controller functions."""
    
    def setUp(self):
        """Set up test data and mock WeatherService for each test."""
        # Create mock UUIDs for consistent testing
        self.location_id = uuid.uuid4()
        self.city_id = uuid.uuid4()
        self.report_id = uuid.uuid4()
        self.condition_id = uuid.uuid4()
        
        # Sample data for responses
        self.weather_report = {
            "id": str(self.report_id),
            "city": "London",
            "temperature": 20.5,
            "temperature_current": 20.5,  # Both versions may appear in service response
            "temperature_unit": "celsius",
            "condition": "Sunny",
            "timestamp": "2023-06-01T12:00:00+00:00",
            "humidity": 65.0,
            "location_id": str(self.location_id),
            "source": "Test"
        }
        
        self.city_summaries = {
            "cities": [
                {
                    "city": "London",
                    "temperature": 20.5,
                    "condition": "Sunny",
                    "timestamp": "2023-06-01T12:00:00+00:00"
                }
            ]
        }
        
        self.request_body = {
            "city": "London",
            "temperature": 20.5,
            "condition": "Sunny",
            "timestamp": "2023-06-01T12:00:00Z",
            "humidity": 65.0
        }
        
        self.update_body = {
            "temperature": 22.5,
            "condition": "Cloudy",
            "timestamp": "2023-06-01T14:00:00Z"
        }
        
        # Set up patcher for WeatherService
        self.weather_service_patcher = patch('api.controllers.weather_controller.WeatherService')
        
        # Start patcher and get mock object
        self.mock_weather_service = self.weather_service_patcher.start()
    
    def tearDown(self):
        """Clean up patchers after each test."""
        self.weather_service_patcher.stop()
    
    def test_add_weather_report_success(self):
        """Test adding a new weather report successfully."""
        # Set up mock
        self.mock_weather_service.add_weather_report.return_value = (self.weather_report, None)
        
        # Call function
        result, status_code = add_weather_report(self.request_body)
        
        # Assertions
        self.assertEqual(status_code, 201)
        self.assertEqual(result, self.weather_report)
        
        # Verify service interactions
        self.mock_weather_service.add_weather_report.assert_called_once_with(
            city_name="London",
            temperature=20.5,
            timestamp_str="2023-06-01T12:00:00Z",
            condition_name="Sunny",
            humidity=65.0
        )
    
    def test_add_weather_report_city_not_found(self):
        """Test adding a weather report when the city is not found."""
        # Set up mock
        error_msg = "City 'NonExistentCity' not found"
        self.mock_weather_service.add_weather_report.return_value = (None, error_msg)
        
        # Test data
        body = {
            "city": "NonExistentCity",
            "temperature": 20.5,
            "condition": "Sunny",
            "timestamp": "2023-06-01T12:00:00Z"
        }
        
        # Call function
        result, status_code = add_weather_report(body)
        
        # Assertions
        self.assertEqual(status_code, 404)
        self.assertEqual(result.get('error'), 'Resource not found')
        self.assertEqual(result.get('detail'), error_msg)
    
    def test_add_weather_report_invalid_timestamp(self):
        """Test adding a weather report with an invalid timestamp format."""
        # Set up mock
        error_msg = "Invalid timestamp format"
        self.mock_weather_service.add_weather_report.return_value = (None, error_msg)
        
        # Test data
        body = {
            "city": "London",
            "temperature": 20.5,
            "condition": "Sunny",
            "timestamp": "invalid-timestamp"
        }
        
        # Call function
        result, status_code = add_weather_report(body)
        
        # Assertions
        self.assertEqual(status_code, 400)
        self.assertEqual(result.get('error'), 'Validation error')
        self.assertIn('timestamp', result.get('detail'))
    
    def test_get_all_city_summaries_success(self):
        """Test getting summaries for all cities successfully."""
        # Set up mock
        self.mock_weather_service.get_all_city_summaries.return_value = (self.city_summaries, None)
        
        # Call function
        result, status_code = get_all_city_summaries()
        
        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(result, self.city_summaries)
        
        # Verify service interactions
        self.mock_weather_service.get_all_city_summaries.assert_called_once()
    
    def test_get_all_city_summaries_error(self):
        """Test getting summaries when an error occurs."""
        # Set up mock
        error_msg = "Internal error: some error"
        self.mock_weather_service.get_all_city_summaries.return_value = (None, error_msg)
        
        # Call function
        result, status_code = get_all_city_summaries()
        
        # Assertions
        self.assertEqual(status_code, 500)
        self.assertEqual(result.get('error'), 'Internal server error')
        self.assertEqual(result.get('detail'), error_msg)
    
    def test_get_city_weather_success(self):
        """Test getting weather for a specific city successfully."""
        # Set up mock
        self.mock_weather_service.get_city_weather.return_value = (self.weather_report, None)
        
        # Call function
        result, status_code = get_city_weather("London")
        
        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(result, self.weather_report)
        
        # Verify service interactions
        self.mock_weather_service.get_city_weather.assert_called_once_with(city_name="London")
    
    def test_get_city_weather_city_not_found(self):
        """Test getting weather when the city is not found."""
        # Set up mock
        error_msg = "City 'NonExistentCity' not found"
        self.mock_weather_service.get_city_weather.return_value = (None, error_msg)
        
        # Call function
        result, status_code = get_city_weather("NonExistentCity")
        
        # Assertions
        self.assertEqual(status_code, 404)
        self.assertEqual(result.get('error'), 'Resource not found')
        self.assertEqual(result.get('detail'), error_msg)
    
    def test_get_city_weather_no_reports(self):
        """Test getting weather when the city exists but has no reports."""
        # Set up mock
        error_msg = "No weather reports found for city 'London'"
        self.mock_weather_service.get_city_weather.return_value = (None, error_msg)
        
        # Call function
        result, status_code = get_city_weather("London")
        
        # Assertions
        self.assertEqual(status_code, 404)
        self.assertEqual(result.get('error'), 'Resource not found')
        self.assertEqual(result.get('detail'), error_msg)
    
    def test_update_city_weather_success(self):
        """Test updating weather for a specific city successfully."""
        # Prepare updated report
        updated_report = dict(self.weather_report)
        updated_report["temperature"] = 22.5
        updated_report["condition"] = "Cloudy"
        updated_report["timestamp"] = "2023-06-01T14:00:00+00:00"
        
        # Set up mock
        self.mock_weather_service.update_city_weather.return_value = (updated_report, None)
        
        # Call function
        result, status_code = update_city_weather("London", self.update_body)
        
        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(result, updated_report)
        
        # Verify service interactions
        self.mock_weather_service.update_city_weather.assert_called_once_with(
            city_name="London",
            updates=self.update_body
        )
    
    def test_update_city_weather_city_not_found(self):
        """Test updating weather when the city is not found."""
        # Set up mock
        error_msg = "City 'NonExistentCity' not found"
        self.mock_weather_service.update_city_weather.return_value = (None, error_msg)
        
        # Call function
        result, status_code = update_city_weather("NonExistentCity", self.update_body)
        
        # Assertions
        self.assertEqual(status_code, 404)
        self.assertEqual(result.get('error'), 'Resource not found')
        self.assertEqual(result.get('detail'), error_msg)
    
    def test_update_city_weather_invalid_timestamp(self):
        """Test updating weather with an invalid timestamp format."""
        # Set up mock
        error_msg = "Invalid timestamp format"
        self.mock_weather_service.update_city_weather.return_value = (None, error_msg)
        
        # Test data
        invalid_body = {
            "temperature": 22.5,
            "condition": "Cloudy",
            "timestamp": "invalid-timestamp"
        }
        
        # Call function
        result, status_code = update_city_weather("London", invalid_body)
        
        # Assertions
        self.assertEqual(status_code, 400)
        self.assertEqual(result.get('error'), 'Validation error')
        self.assertIn('timestamp', result.get('detail'))
    
    def test_delete_city_weather_success(self):
        """Test deleting all weather reports for a city successfully."""
        # Set up mock
        self.mock_weather_service.delete_city_weather.return_value = (True, None)
        
        # Call function
        result, status_code = delete_city_weather("London")
        
        # Assertions
        self.assertEqual(status_code, 204)
        self.assertEqual(result, "")
        
        # Verify service interactions
        self.mock_weather_service.delete_city_weather.assert_called_once_with(city_name="London")
    
    def test_delete_city_weather_city_not_found(self):
        """Test deleting weather reports when the city is not found."""
        # Set up mock
        error_msg = "City 'NonExistentCity' not found"
        self.mock_weather_service.delete_city_weather.return_value = (False, error_msg)
        
        # Call function
        result, status_code = delete_city_weather("NonExistentCity")
        
        # Assertions
        self.assertEqual(status_code, 404)
        self.assertEqual(result.get('error'), 'Resource not found')
        self.assertEqual(result.get('detail'), error_msg)
    
    def test_delete_city_weather_no_reports(self):
        """Test deleting weather reports when the city exists but has no reports."""
        # Set up mock
        error_msg = "No weather reports found for city 'London'"
        self.mock_weather_service.delete_city_weather.return_value = (False, error_msg)
        
        # Call function
        result, status_code = delete_city_weather("London")
        
        # Assertions
        self.assertEqual(status_code, 404)
        self.assertEqual(result.get('error'), 'Resource not found')
        self.assertEqual(result.get('detail'), error_msg)


if __name__ == '__main__':
    unittest.main() 