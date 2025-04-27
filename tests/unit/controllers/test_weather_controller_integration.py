import unittest
import uuid
from datetime import datetime, timezone
import logging

from api.controllers.weather_controller import (
    add_weather_report, get_all_city_summaries, 
    get_city_weather, update_city_weather, delete_city_weather
)
from api.models.domain import (
    City, Location, TemperatureUnit
)
from api.repositories.memory_repository import (
    city_repository, location_repository, report_repository, 
    condition_repository, report_condition_repository
)

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestWeatherControllerIntegration(unittest.TestCase):
    """Integration tests for the weather controller functions with actual repositories."""
    
    def setUp(self):
        """Set up test data in the repositories for each test."""
        # Clear all repositories
        location_repository.clear()
        city_repository.clear()
        report_repository.clear()
        condition_repository.clear()
        report_condition_repository.clear()
        
        # Create test location
        self.test_location = Location(
            name="London Area",
            latitude=51.5074,
            longitude=-0.1278,
            elevation=11.0,
            timezone="Europe/London"
        )
        self.stored_location = location_repository.add(self.test_location)
        
        # Create test city
        self.test_city = City(
            name="London",
            country="UK",
            location_id=self.stored_location.id
        )
        self.stored_city = city_repository.add(self.test_city)
        
        # Create another test city for multiple city tests
        self.test_location2 = Location(
            name="Paris Area",
            latitude=48.8566,
            longitude=2.3522,
            elevation=35.0,
            timezone="Europe/Paris"
        )
        self.stored_location2 = location_repository.add(self.test_location2)
        
        self.test_city2 = City(
            name="Paris",
            country="France",
            location_id=self.stored_location2.id
        )
        self.stored_city2 = city_repository.add(self.test_city2)
        
        logger.info(f"Set up test data: London (ID: {self.stored_city.id}) and Paris (ID: {self.stored_city2.id})")
    
    def tearDown(self):
        """Clean up repositories after each test."""
        location_repository.clear()
        city_repository.clear()
        report_repository.clear()
        condition_repository.clear()
        report_condition_repository.clear()
        logger.info("Cleared all repositories")
    
    def test_full_weather_lifecycle(self):
        """Test the full lifecycle of weather reports: add, get, update, delete."""
        # 1. Add a weather report
        add_body = {
            "city": "London",
            "temperature": 20.5,
            "condition": "Sunny",
            "timestamp": "2023-06-01T12:00:00Z"
        }
        
        add_result, add_status = add_weather_report(add_body)
        logger.info(f"Add result: {add_result}")
        
        self.assertEqual(add_status, 201)
        self.assertEqual(add_result.get('city'), 'London')
        self.assertEqual(add_result.get('temperature'), 20.5)
        self.assertEqual(add_result.get('condition'), 'Sunny')
        
        report_id = add_result.get('id')
        self.assertIsNotNone(report_id)
        
        # 2. Get the weather for the city
        get_result, get_status = get_city_weather("London")
        logger.info(f"Get result: {get_result}")
        
        self.assertEqual(get_status, 200)
        self.assertEqual(get_result.get('city'), 'London')
        self.assertEqual(get_result.get('temperature'), 20.5)
        self.assertEqual(get_result.get('condition'), 'Sunny')
        
        # 3. Get all city summaries
        summaries_result, summaries_status = get_all_city_summaries()
        logger.info(f"Summary result: {summaries_result}")
        
        self.assertEqual(summaries_status, 200)
        self.assertIn('cities', summaries_result)
        
        london_found = False
        for city_summary in summaries_result['cities']:
            if city_summary['city'] == 'London':
                london_found = True
                self.assertEqual(city_summary['temperature'], 20.5)
                self.assertEqual(city_summary['condition'], 'Sunny')
        
        self.assertTrue(london_found, "London should be in the city summaries")
        
        # 4. Update the weather report
        update_body = {
            "temperature": 22.5,
            "condition": "Cloudy",
            "timestamp": "2023-06-01T14:00:00Z"
        }
        
        update_result, update_status = update_city_weather("London", update_body)
        logger.info(f"Update result: {update_result}")
        
        self.assertEqual(update_status, 200)
        self.assertEqual(update_result.get('city'), 'London')
        self.assertEqual(update_result.get('temperature'), 22.5)
        self.assertEqual(update_result.get('condition'), 'Cloudy')
        
        # 5. Verify the update with get
        get_updated_result, _ = get_city_weather("London")
        logger.info(f"Get updated result: {get_updated_result}")
        
        self.assertEqual(get_updated_result.get('temperature'), 22.5)
        self.assertEqual(get_updated_result.get('condition'), 'Cloudy')
        
        # 6. Delete the weather report
        delete_result, delete_status = delete_city_weather("London")
        logger.info(f"Delete status: {delete_status}")
        
        self.assertEqual(delete_status, 204)
        self.assertEqual(delete_result, "")
        
        # 7. Verify the deletion
        get_after_delete_result, get_after_delete_status = get_city_weather("London")
        logger.info(f"Get after delete: {get_after_delete_result}, status: {get_after_delete_status}")
        
        self.assertEqual(get_after_delete_status, 404)
        self.assertEqual(get_after_delete_result.get('error'), 'Resource not found')
    
    def test_multiple_cities(self):
        """Test handling of multiple cities in the system."""
        # Add weather reports for both cities
        london_body = {
            "city": "London",
            "temperature": 20.5,
            "condition": "Sunny",
            "timestamp": "2023-06-01T12:00:00Z"
        }
        
        paris_body = {
            "city": "Paris",
            "temperature": 25.0,
            "condition": "Cloudy",
            "timestamp": "2023-06-01T12:30:00Z"
        }
        
        add_weather_report(london_body)
        add_weather_report(paris_body)
        
        # Get summaries and check both cities are there
        summaries_result, _ = get_all_city_summaries()
        self.assertEqual(len(summaries_result['cities']), 2)
        
        cities = {city['city'] for city in summaries_result['cities']}
        self.assertIn('London', cities)
        self.assertIn('Paris', cities)
        
        # Get specific city weather and check it's correct
        london_result, _ = get_city_weather("London")
        paris_result, _ = get_city_weather("Paris")
        
        self.assertEqual(london_result.get('temperature'), 20.5)
        self.assertEqual(london_result.get('condition'), 'Sunny')
        
        self.assertEqual(paris_result.get('temperature'), 25.0)
        self.assertEqual(paris_result.get('condition'), 'Cloudy')
    
    def test_add_weather_report_for_new_city(self):
        """Test adding a weather report for a city that doesn't exist yet."""
        # Ensure the city doesn't exist before the test
        cities_before = city_repository.get_all()
        city_names_before = {city.name for city in cities_before}
        
        # Choose a city name that doesn't exist
        new_city_name = "TestNewCity"
        self.assertNotIn(new_city_name, city_names_before)
        
        # Add a weather report for the new city
        new_city_body = {
            "city": new_city_name,
            "temperature": 18.5,
            "condition": "Rainy",
            "timestamp": "2023-06-01T15:00:00Z"
        }
        
        result, status_code = add_weather_report(new_city_body)
        
        # Verify the request was successful
        self.assertEqual(status_code, 201)
        self.assertEqual(result.get('city'), new_city_name)
        self.assertEqual(result.get('temperature'), 18.5)
        self.assertEqual(result.get('condition'), 'Rainy')
        
        # Verify the city was created
        cities_after = city_repository.get_all()
        city_names_after = {city.name for city in cities_after}
        self.assertIn(new_city_name, city_names_after)
        
        # Verify we can get the weather for this new city
        weather_result, weather_status = get_city_weather(new_city_name)
        self.assertEqual(weather_status, 200)
        self.assertEqual(weather_result.get('city'), new_city_name)
        self.assertEqual(weather_result.get('temperature'), 18.5)
        self.assertEqual(weather_result.get('condition'), 'Rainy')
    
    def test_error_handling(self):
        """Test error handling in the controller."""
        # Test city not found
        city_not_found_result, city_not_found_status = get_city_weather("NonExistentCity")
        self.assertEqual(city_not_found_status, 404)
        self.assertEqual(city_not_found_result.get('error'), 'Resource not found')
        
        # Test invalid timestamp
        invalid_body = {
            "city": "London",
            "temperature": 20.5,
            "condition": "Sunny",
            "timestamp": "invalid-timestamp"
        }
        
        invalid_result, invalid_status = add_weather_report(invalid_body)
        self.assertEqual(invalid_status, 400)
        self.assertEqual(invalid_result.get('error'), 'Validation error')
        
        # Test no reports for a city
        # This should no longer happen since we now create cities
        # when they don't exist, but we still need to test for no reports
        
        # Create a city without reports
        test_location = Location(
            name="EmptyCity Area",
            latitude=0.0,
            longitude=0.0,
            elevation=0.0,
            timezone="UTC"
        )
        stored_location = location_repository.add(test_location)
        
        test_city = City(
            name="EmptyCity",
            country="Unknown",
            location_id=stored_location.id
        )
        city_repository.add(test_city)
        
        # Check that we get a 404 when trying to get weather for a city with no reports
        no_reports_result, no_reports_status = get_city_weather("EmptyCity")
        self.assertEqual(no_reports_status, 404)
        self.assertEqual(no_reports_result.get('error'), 'Resource not found')


if __name__ == '__main__':
    unittest.main() 