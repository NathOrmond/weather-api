import unittest
from datetime import datetime, timezone
import uuid

from api.models.domain import (
    Location, City, Condition, Report, ReportCondition,
    ConditionType, IntensityLevel, TemperatureUnit
)


class TestDomainToDictMethods(unittest.TestCase):
    """Test suite for the to_dict methods in domain model classes."""
    
    def setUp(self):
        """Set up test data for each test."""
        # Create UUIDs for testing
        self.location_id = uuid.uuid4()
        self.city_id = uuid.uuid4()
        self.report_id = uuid.uuid4()
        self.condition_id = uuid.uuid4()
        self.report_condition_id = uuid.uuid4()
        
        # Create sample timestamp
        self.test_timestamp = datetime(2023, 6, 1, 12, 0, tzinfo=timezone.utc)
    
    def test_location_to_dict(self):
        """Test the Location.to_dict method."""
        location = Location(
            id=self.location_id,
            name="London Area",
            latitude=51.5074,
            longitude=-0.1278,
            elevation=11.0,
            timezone="Europe/London"
        )
        
        location_dict = location.to_dict()
        
        self.assertEqual(location_dict["id"], str(self.location_id))
        self.assertEqual(location_dict["name"], "London Area")
        self.assertEqual(location_dict["latitude"], 51.5074)
        self.assertEqual(location_dict["longitude"], -0.1278)
        self.assertEqual(location_dict["elevation"], 11.0)
        self.assertEqual(location_dict["timezone"], "Europe/London")
    
    def test_city_to_dict(self):
        """Test the City.to_dict method."""
        city = City(
            id=self.city_id,
            name="London",
            country="UK",
            location_id=self.location_id
        )
        
        city_dict = city.to_dict()
        
        self.assertEqual(city_dict["id"], str(self.city_id))
        self.assertEqual(city_dict["name"], "London")
        self.assertEqual(city_dict["country"], "UK")
        self.assertEqual(city_dict["location_id"], str(self.location_id))
    
    def test_condition_to_dict(self):
        """Test the Condition.to_dict method."""
        condition = Condition(
            id=self.condition_id,
            name="Sunny",
            type=ConditionType.SUNNY,
            intensity=IntensityLevel.MODERATE
        )
        
        condition_dict = condition.to_dict()
        
        self.assertEqual(condition_dict["id"], str(self.condition_id))
        self.assertEqual(condition_dict["name"], "Sunny")
        self.assertEqual(condition_dict["type"], "sunny")
        self.assertEqual(condition_dict["intensity"], "moderate")
    
    def test_report_to_dict(self):
        """Test the Report.to_dict method."""
        report = Report(
            id=self.report_id,
            location_id=self.location_id,
            timestamp=self.test_timestamp,
            source="Test",
            temperature_current=20.5,
            temperature_unit=TemperatureUnit.CELSIUS,
            humidity=65.0
        )
        
        report_dict = report.to_dict()
        
        self.assertEqual(report_dict["id"], str(self.report_id))
        self.assertEqual(report_dict["location_id"], str(self.location_id))
        self.assertEqual(report_dict["timestamp"], self.test_timestamp.isoformat())
        self.assertEqual(report_dict["source"], "Test")
        self.assertEqual(report_dict["temperature"], 20.5)
        self.assertEqual(report_dict["temperature_unit"], "celsius")
        self.assertEqual(report_dict["humidity"], 65.0)
    
    def test_report_condition_to_dict(self):
        """Test the ReportCondition.to_dict method."""
        report_condition = ReportCondition(
            id=self.report_condition_id,
            report_id=self.report_id,
            condition_id=self.condition_id
        )
        
        report_condition_dict = report_condition.to_dict()
        
        self.assertEqual(report_condition_dict["id"], str(self.report_condition_id))
        self.assertEqual(report_condition_dict["report_id"], str(self.report_id))
        self.assertEqual(report_condition_dict["condition_id"], str(self.condition_id))


if __name__ == '__main__':
    unittest.main() 