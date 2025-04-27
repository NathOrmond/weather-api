import unittest
from unittest.mock import patch

from api.repositories.seed import seed_data
from api.repositories.memory_repository import (
    location_repository,
    city_repository,
    condition_repository,
    report_repository, 
    report_condition_repository
)


class TestSeedData(unittest.TestCase):
    """Test the seeding functionality."""
    
    def setUp(self):
        """Set up test conditions."""
        location_repository.clear()
        city_repository.clear()
        condition_repository.clear()
        report_repository.clear()
        report_condition_repository.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        location_repository.clear()
        city_repository.clear()
        condition_repository.clear()
        report_repository.clear()
        report_condition_repository.clear()
    
    def test_seed_data(self):
        """Test that seed_data populates repositories with expected data."""
        self.assertEqual(len(location_repository.get_all()), 0)
        self.assertEqual(len(city_repository.get_all()), 0)
        self.assertEqual(len(condition_repository.get_all()), 0)
        self.assertEqual(len(report_repository.get_all()), 0)
        self.assertEqual(len(report_condition_repository.get_all()), 0)
        seed_data()
        
        # After seeding, repositories should have data
        # Locations (2 expected: London and Tokyo)
        locations = location_repository.get_all()
        self.assertEqual(len(locations), 2)
        location_names = {loc.name for loc in locations}
        self.assertIn("London Centre", location_names)
        self.assertIn("Tokyo Station", location_names)
        
        # Cities (2 expected: London and Tokyo)
        cities = city_repository.get_all()
        self.assertEqual(len(cities), 2)
        city_names = {city.name for city in cities}
        self.assertIn("London", city_names)
        self.assertIn("Tokyo", city_names)
        
        # Conditions (3 expected: Sunny, Cloudy, Light Rain)
        conditions = condition_repository.get_all()
        self.assertEqual(len(conditions), 3)
        condition_names = {cond.name for cond in conditions}
        self.assertIn("Sunny", condition_names)
        self.assertIn("Cloudy", condition_names)
        self.assertIn("Light Rain", condition_names)
        
        # Reports (3 expected: 2 for London, 1 for Tokyo)
        reports = report_repository.get_all()
        self.assertEqual(len(reports), 3)
        
        # ReportConditions (3 expected: 1 for each report)
        report_conditions = report_condition_repository.get_all()
        self.assertEqual(len(report_conditions), 3)
        
        # Verify relationships: Each city has a valid location
        for city in cities:
            # Find city's location
            city_location = location_repository.get_by_id(city.location_id)
            self.assertIsNotNone(city_location)
            # London should have London Centre location
            if city.name == "London":
                self.assertEqual(city_location.name, "London Centre")
            # Tokyo should have Tokyo Station location
            if city.name == "Tokyo":
                self.assertEqual(city_location.name, "Tokyo Station")
        
        # Verify relationships: Each report condition links to a valid report and condition
        for rc in report_conditions:
            report = report_repository.get_by_id(rc.report_id)
            condition = condition_repository.get_by_id(rc.condition_id)
            self.assertIsNotNone(report)
            self.assertIsNotNone(condition)
    
    @patch('api.repositories.memory_repository.location_repository.add')
    def test_seed_data_error_handling(self, mock_add):
        """Test that seed_data handles errors appropriately."""
        # Make location_repository.add raise an exception
        mock_add.side_effect = ValueError("Test error")
        # Run the seed function
        seed_data()
        # Verify that the method was called
        self.assertTrue(mock_add.called)
        # No data should be in the repositories due to the error
        self.assertEqual(len(city_repository.get_all()), 0)
        self.assertEqual(len(condition_repository.get_all()), 0)
        self.assertEqual(len(report_repository.get_all()), 0)
        self.assertEqual(len(report_condition_repository.get_all()), 0)


if __name__ == '__main__':
    unittest.main() 