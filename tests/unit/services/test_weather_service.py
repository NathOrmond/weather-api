import unittest
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime, timezone

from api.services.weather_service import WeatherService
from api.models.domain import (
    City, Location, Report, Condition, ReportCondition,
    ConditionType, IntensityLevel, TemperatureUnit
)


class TestWeatherService(unittest.TestCase):
    """Test cases for the WeatherService class."""
    
    def setUp(self):
        """Set up test data and mock repositories for each test."""
        # Create mock UUIDs for consistent testing
        self.location_id = uuid.uuid4()
        self.city_id = uuid.uuid4()
        self.report_id = uuid.uuid4()
        self.condition_id = uuid.uuid4()
        self.report_condition_id = uuid.uuid4()
        
        # Create sample domain objects
        self.test_location = Location(
            id=self.location_id,
            name="London Area",
            latitude=51.5074,
            longitude=-0.1278,
            elevation=11.0,
            timezone="Europe/London"
        )
        
        self.test_city = City(
            id=self.city_id,
            name="London",
            country="UK",
            location_id=self.location_id
        )
        
        self.test_report = Report(
            id=self.report_id,
            location_id=self.location_id,
            timestamp=datetime(2023, 6, 1, 12, 0, tzinfo=timezone.utc),
            source="Test",
            temperature_current=20.5,
            temperature_unit=TemperatureUnit.CELSIUS,
            humidity=65.0
        )
        
        self.test_condition = Condition(
            id=self.condition_id,
            name="Sunny",
            type=ConditionType.SUNNY,
            intensity=IntensityLevel.MODERATE
        )
        
        self.test_report_condition = ReportCondition(
            id=self.report_condition_id,
            report_id=self.report_id,
            condition_id=self.condition_id
        )
        
        # Set up patcher for repositories
        self.city_repo_patcher = patch('api.services.weather_service.city_repository')
        self.location_repo_patcher = patch('api.services.weather_service.location_repository')
        self.report_repo_patcher = patch('api.services.weather_service.report_repository')
        self.condition_repo_patcher = patch('api.services.weather_service.condition_repository')
        self.report_condition_repo_patcher = patch('api.services.weather_service.report_condition_repository')
        
        # Start patchers and get mock objects
        self.mock_city_repo = self.city_repo_patcher.start()
        self.mock_location_repo = self.location_repo_patcher.start()
        self.mock_report_repo = self.report_repo_patcher.start()
        self.mock_condition_repo = self.condition_repo_patcher.start()
        self.mock_report_condition_repo = self.report_condition_repo_patcher.start()
    
    def tearDown(self):
        """Clean up patchers after each test."""
        self.city_repo_patcher.stop()
        self.location_repo_patcher.stop()
        self.report_repo_patcher.stop()
        self.condition_repo_patcher.stop()
        self.report_condition_repo_patcher.stop()
    
    def test_add_weather_report_success(self):
        """Test adding a new weather report successfully."""
        # Set up mocks
        self.mock_city_repo.find_by_name.return_value = self.test_city
        self.mock_report_repo.add.return_value = self.test_report
        self.mock_condition_repo.find_by_name.return_value = self.test_condition
        self.mock_report_condition_repo.add.return_value = self.test_report_condition
        
        # Call method
        result, error_msg = WeatherService.add_weather_report(
            city_name="London",
            temperature=20.5,
            timestamp_str="2023-06-01T12:00:00Z",
            condition_name="Sunny",
            humidity=65.0
        )
        
        # Assertions
        self.assertIsNone(error_msg)
        self.assertIsNotNone(result)
        self.assertEqual(str(result.get("id")), str(self.report_id))
        self.assertEqual(result.get("city"), "London")
        self.assertEqual(result.get("temperature"), 20.5)
        self.assertEqual(result.get("condition"), "Sunny")
        
        # Verify repository interactions
        self.mock_city_repo.find_by_name.assert_called_once_with("London")
        self.mock_report_repo.add.assert_called_once()
        self.mock_condition_repo.find_by_name.assert_called_once_with("Sunny")
        self.mock_report_condition_repo.add.assert_called_once()
    
    def test_add_weather_report_new_city(self):
        """Test adding a weather report for a non-existent city creates the city."""
        # Set up mocks for city not found -> create new city
        self.mock_city_repo.find_by_name.return_value = None
        
        # Mocks for location creation
        new_location = Location(
            id=uuid.uuid4(),
            name="NewCity Area",
            latitude=0.0,
            longitude=0.0,
            elevation=0.0,
            timezone="UTC"
        )
        self.mock_location_repo.add.return_value = new_location
        
        # Mocks for city creation
        new_city = City(
            id=uuid.uuid4(),
            name="NewCity",
            country="Unknown",
            location_id=new_location.id
        )
        self.mock_city_repo.add.return_value = new_city
        
        # Mocks for report creation
        self.mock_report_repo.add.return_value = self.test_report
        self.mock_condition_repo.find_by_name.return_value = self.test_condition
        self.mock_report_condition_repo.add.return_value = self.test_report_condition
        
        # Call method
        result, error_msg = WeatherService.add_weather_report(
            city_name="NewCity",
            temperature=22.5,
            timestamp_str="2023-06-01T14:00:00Z",
            condition_name="Sunny",
            humidity=70.0
        )
        
        # Assertions
        self.assertIsNone(error_msg)
        self.assertIsNotNone(result)
        self.assertEqual(str(result.get("id")), str(self.report_id))
        self.assertEqual(result.get("city"), "NewCity")
        self.assertEqual(result.get("temperature"), 20.5)
        self.assertEqual(result.get("condition"), "Sunny")
        
        # Verify repository interactions
        self.mock_city_repo.find_by_name.assert_called_once_with("NewCity")
        self.mock_location_repo.add.assert_called_once()
        self.mock_city_repo.add.assert_called_once()
        self.mock_report_repo.add.assert_called_once()
        self.mock_condition_repo.find_by_name.assert_called_once_with("Sunny")
        self.mock_report_condition_repo.add.assert_called_once()
    
    def test_add_weather_report_city_not_found(self):
        """Test adding a weather report when the city is not found."""
        # This test is no longer relevant since we now create cities if they don't exist
        # Keeping it as a placeholder to clarify the change in behavior
        pass
    
    def test_add_weather_report_invalid_timestamp(self):
        """Test adding a weather report with an invalid timestamp format."""
        # Set up mocks
        self.mock_city_repo.find_by_name.return_value = self.test_city
        
        # Call method
        result, error_msg = WeatherService.add_weather_report(
            city_name="London",
            temperature=20.5,
            timestamp_str="invalid-timestamp"
        )
        
        # Assertions
        self.assertIsNone(result)
        self.assertIsNotNone(error_msg)
        self.assertIn("Invalid timestamp format", error_msg)
        
        # Verify repository interactions
        self.mock_city_repo.find_by_name.assert_called_once_with("London")
        self.mock_report_repo.add.assert_not_called()
    
    def test_get_all_city_summaries_success(self):
        """Test getting summaries for all cities successfully."""
        # Set up mocks
        self.mock_city_repo.get_all.return_value = [self.test_city]
        self.mock_report_repo.find_by_location_id.return_value = [self.test_report]
        self.mock_report_condition_repo.find_by_report_id.return_value = [self.test_report_condition]
        self.mock_condition_repo.get_by_id.return_value = self.test_condition
        
        # Call method
        result, error_msg = WeatherService.get_all_city_summaries()
        
        # Assertions
        self.assertIsNone(error_msg)
        self.assertIsNotNone(result)
        self.assertIn("cities", result)
        self.assertEqual(len(result["cities"]), 1)
        self.assertEqual(result["cities"][0]["city"], "London")
        self.assertEqual(result["cities"][0]["temperature"], 20.5)
        self.assertEqual(result["cities"][0]["condition"], "Sunny")
        
        # Verify repository interactions
        self.mock_city_repo.get_all.assert_called_once()
        self.mock_report_repo.find_by_location_id.assert_called_once_with(self.location_id, latest_only=True)
        self.mock_report_condition_repo.find_by_report_id.assert_called_once_with(self.report_id)
        self.mock_condition_repo.get_by_id.assert_called_once_with(self.condition_id)
    
    def test_get_city_weather_success(self):
        """Test getting weather for a specific city successfully."""
        # Set up mocks
        self.mock_city_repo.find_by_name.return_value = self.test_city
        self.mock_report_repo.find_by_location_id.return_value = [self.test_report]
        self.mock_report_condition_repo.find_by_report_id.return_value = [self.test_report_condition]
        self.mock_condition_repo.get_by_id.return_value = self.test_condition
        
        # Call method
        result, error_msg = WeatherService.get_city_weather(city_name="London")
        
        # Assertions
        self.assertIsNone(error_msg)
        self.assertIsNotNone(result)
        self.assertEqual(str(result.get("id")), str(self.report_id))
        self.assertEqual(result.get("city"), "London")
        self.assertEqual(result.get("temperature"), 20.5)
        self.assertEqual(result.get("condition"), "Sunny")
        
        # Verify repository interactions
        self.mock_city_repo.find_by_name.assert_called_once_with("London")
        self.mock_report_repo.find_by_location_id.assert_called_once_with(self.location_id, latest_only=True)
        self.mock_report_condition_repo.find_by_report_id.assert_called_once_with(self.report_id)
        self.mock_condition_repo.get_by_id.assert_called_once_with(self.condition_id)
    
    def test_get_city_weather_city_not_found(self):
        """Test getting weather when the city is not found."""
        # Set up mocks
        self.mock_city_repo.find_by_name.return_value = None
        
        # Call method
        result, error_msg = WeatherService.get_city_weather(city_name="NonExistentCity")
        
        # Assertions
        self.assertIsNone(result)
        self.assertIsNotNone(error_msg)
        self.assertIn("City 'NonExistentCity' not found", error_msg)
        
        # Verify repository interactions
        self.mock_city_repo.find_by_name.assert_called_once_with("NonExistentCity")
        self.mock_report_repo.find_by_location_id.assert_not_called()
    
    def test_update_city_weather_success(self):
        """Test updating weather for a specific city successfully."""
        # Prepare updated report
        updated_report = Report(
            id=self.report_id,
            location_id=self.location_id,
            timestamp=datetime(2023, 6, 1, 14, 0, tzinfo=timezone.utc),
            source="Test",
            temperature_current=22.5,
            temperature_unit=TemperatureUnit.CELSIUS,
            humidity=70.0
        )
        
        # Set up mocks
        self.mock_city_repo.find_by_name.return_value = self.test_city
        self.mock_report_repo.find_by_location_id.return_value = [self.test_report]
        self.mock_report_repo.update.return_value = updated_report
        self.mock_report_condition_repo.find_by_report_id.return_value = [self.test_report_condition]
        self.mock_condition_repo.find_by_name.return_value = self.test_condition
        self.mock_report_condition_repo.add.return_value = self.test_report_condition
        
        # Call method
        result, error_msg = WeatherService.update_city_weather(
            city_name="London",
            updates={
                "temperature": 22.5,
                "condition": "Sunny",
                "timestamp": "2023-06-01T14:00:00Z"
            }
        )
        
        # Assertions
        self.assertIsNone(error_msg)
        self.assertIsNotNone(result)
        self.assertEqual(str(result.get("id")), str(self.report_id))
        self.assertEqual(result.get("city"), "London")
        self.assertEqual(result.get("temperature"), 22.5)
        self.assertEqual(result.get("condition"), "Sunny")
        
        # Verify repository interactions
        self.mock_city_repo.find_by_name.assert_called_once_with("London")
        self.mock_report_repo.find_by_location_id.assert_called_once_with(self.location_id, latest_only=True)
        self.mock_report_repo.update.assert_called_once()
    
    def test_delete_city_weather_success(self):
        """Test deleting all weather reports for a city successfully."""
        # Set up mocks
        self.mock_city_repo.find_by_name.return_value = self.test_city
        self.mock_report_repo.find_by_location_id.return_value = [self.test_report]
        self.mock_report_condition_repo.find_by_report_id.return_value = [self.test_report_condition]
        self.mock_report_condition_repo.delete.return_value = True
        self.mock_report_repo.delete.return_value = True
        
        # Call method
        success, error_msg = WeatherService.delete_city_weather(city_name="London")
        
        # Assertions
        self.assertTrue(success)
        self.assertIsNone(error_msg)
        
        # Verify repository interactions
        self.mock_city_repo.find_by_name.assert_called_once_with("London")
        self.mock_report_repo.find_by_location_id.assert_called_once_with(self.location_id)
        self.mock_report_condition_repo.find_by_report_id.assert_called_once_with(self.report_id)
        self.mock_report_condition_repo.delete.assert_called_once_with(self.report_condition_id)
        self.mock_report_repo.delete.assert_called_once_with(self.report_id)
    
    def test_add_condition_to_report(self):
        """Test the _add_condition_to_report helper method."""
        # Set up mocks
        self.mock_condition_repo.find_by_name.return_value = self.test_condition
        self.mock_report_condition_repo.add.return_value = self.test_report_condition
        
        # Call method
        error_msg = WeatherService._add_condition_to_report("Sunny", self.report_id)
        
        # Assertions
        self.assertIsNone(error_msg)
        
        # Verify repository interactions
        self.mock_condition_repo.find_by_name.assert_called_once_with("Sunny")
        self.mock_report_condition_repo.add.assert_called_once()
    
    def test_get_condition_for_report(self):
        """Test the _get_condition_for_report helper method."""
        # Set up mocks
        self.mock_report_condition_repo.find_by_report_id.return_value = [self.test_report_condition]
        self.mock_condition_repo.get_by_id.return_value = self.test_condition
        
        # Call method
        condition_name = WeatherService._get_condition_for_report(self.report_id)
        
        # Assertions
        self.assertEqual(condition_name, "Sunny")
        
        # Verify repository interactions
        self.mock_report_condition_repo.find_by_report_id.assert_called_once_with(self.report_id)
        self.mock_condition_repo.get_by_id.assert_called_once_with(self.condition_id)
    
    def test_remove_conditions_for_report(self):
        """Test the _remove_conditions_for_report helper method."""
        # Set up mocks
        self.mock_report_condition_repo.find_by_report_id.return_value = [self.test_report_condition]
        self.mock_report_condition_repo.delete.return_value = True
        
        # Call method
        WeatherService._remove_conditions_for_report(self.report_id)
        
        # Verify repository interactions
        self.mock_report_condition_repo.find_by_report_id.assert_called_once_with(self.report_id)
        self.mock_report_condition_repo.delete.assert_called_once_with(self.report_condition_id)


if __name__ == '__main__':
    unittest.main() 