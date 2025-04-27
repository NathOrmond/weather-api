import unittest
from datetime import datetime
from uuid import uuid4

from api.schemas import (
    LocationSchema,
    CitySchema,
    ConditionSchema,
    ReportSchema,
    ReportConditionSchema
)
from api.models.domain import (
    Location,
    City,
    Condition,
    Report,
    ReportCondition,
    ConditionType,
    IntensityLevel,
    TemperatureUnit
)


class TestLocationSchema(unittest.TestCase):
    """Test cases for the LocationSchema."""

    def setUp(self):
        """Set up test data."""
        self.test_id = uuid4()
        self.valid_data = {
            "name": "London",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "elevation": 35.0,
            "timezone": "Europe/London"
        }
        
    def test_load_valid_data(self):
        """Test loading valid data into a Location model."""
        schema = LocationSchema()
        result = schema.load(self.valid_data)
        
        self.assertIsInstance(result, Location)
        self.assertEqual(result.name, "London")
        self.assertEqual(result.latitude, 51.5074)
        self.assertEqual(result.longitude, -0.1278)
        self.assertEqual(result.elevation, 35.0)
        self.assertEqual(result.timezone, "Europe/London")
    
    def test_dump_location(self):
        """Test serializing a Location model."""
        location = Location(
            id=self.test_id,
            name="London",
            latitude=51.5074,
            longitude=-0.1278,
            elevation=35.0,
            timezone="Europe/London"
        )
        
        schema = LocationSchema()
        result = schema.dump(location)
        
        self.assertEqual(result["id"], str(self.test_id))
        self.assertEqual(result["name"], "London")
        self.assertEqual(result["latitude"], 51.5074)
        self.assertEqual(result["longitude"], -0.1278)
        self.assertEqual(result["elevation"], 35.0)
        self.assertEqual(result["timezone"], "Europe/London")
    
    def test_invalid_latitude(self):
        """Test schema validation for latitude outside valid range."""
        schema = LocationSchema()
        invalid_data = self.valid_data.copy()
        invalid_data["latitude"] = 100.0  # Outside valid range of -90 to 90
        
        with self.assertRaises(Exception) as context:
            schema.load(invalid_data)
        
        self.assertIn("latitude", str(context.exception))


class TestCitySchema(unittest.TestCase):
    """Test cases for the CitySchema."""

    def setUp(self):
        """Set up test data."""
        self.test_id = uuid4()
        self.location_id = uuid4()
        self.valid_data = {
            "name": "London",
            "country": "UK",
            "location_id": str(self.location_id)
        }
        
    def test_load_valid_data(self):
        """Test loading valid data into a City model."""
        schema = CitySchema()
        result = schema.load(self.valid_data)
        
        self.assertIsInstance(result, City)
        self.assertEqual(result.name, "London")
        self.assertEqual(result.country, "UK")
        self.assertEqual(result.location_id, self.location_id)
    
    def test_dump_city(self):
        """Test serializing a City model."""
        city = City(
            id=self.test_id,
            name="London",
            country="UK",
            location_id=self.location_id
        )
        
        schema = CitySchema()
        result = schema.dump(city)
        
        self.assertEqual(result["id"], str(self.test_id))
        self.assertEqual(result["name"], "London")
        self.assertEqual(result["country"], "UK")
        self.assertEqual(result["location_id"], str(self.location_id))


class TestConditionSchema(unittest.TestCase):
    """Test cases for the ConditionSchema."""

    def setUp(self):
        """Set up test data."""
        self.test_id = uuid4()
        self.valid_data = {
            "name": "Heavy Rain",
            "type": "rainy",
            "intensity": "heavy"
        }
        
    def test_load_valid_data(self):
        """Test loading valid data into a Condition model."""
        schema = ConditionSchema()
        result = schema.load(self.valid_data)
        
        self.assertIsInstance(result, Condition)
        self.assertEqual(result.name, "Heavy Rain")
        self.assertEqual(result.type, ConditionType.RAINY)
        self.assertEqual(result.intensity, IntensityLevel.HEAVY)
    
    def test_dump_condition(self):
        """Test serializing a Condition model."""
        condition = Condition(
            id=self.test_id,
            name="Heavy Rain",
            type=ConditionType.RAINY,
            intensity=IntensityLevel.HEAVY
        )
        
        schema = ConditionSchema()
        result = schema.dump(condition)
        
        self.assertEqual(result["id"], str(self.test_id))
        self.assertEqual(result["name"], "Heavy Rain")
        self.assertEqual(result["type"], "rainy")
        self.assertEqual(result["intensity"], "heavy")
    
    def test_invalid_condition_type(self):
        """Test schema validation for invalid condition type."""
        schema = ConditionSchema()
        invalid_data = self.valid_data.copy()
        invalid_data["type"] = "invalid"
        
        with self.assertRaises(Exception) as context:
            schema.load(invalid_data)
        
        self.assertIn("type", str(context.exception))


class TestReportSchema(unittest.TestCase):
    """Test cases for the ReportSchema."""

    def setUp(self):
        """Set up test data."""
        self.test_id = uuid4()
        self.location_id = uuid4()
        self.timestamp = datetime.now()
        self.valid_data = {
            "location_id": str(self.location_id),
            "timestamp": self.timestamp.isoformat(),
            "source": "Weather Station",
            "temperature": 22.5,  # Using 'temperature' in API but maps to 'temperature_current'
            "temperature_unit": "celsius",
            "humidity": 65.0
        }
        
    def test_load_valid_data(self):
        """Test loading valid data into a Report model."""
        schema = ReportSchema()
        result = schema.load(self.valid_data)
        
        self.assertIsInstance(result, Report)
        self.assertEqual(result.location_id, self.location_id)
        self.assertIsInstance(result.timestamp, datetime)
        self.assertEqual(result.source, "Weather Station")
        self.assertEqual(result.temperature_current, 22.5)
        self.assertEqual(result.temperature_unit, TemperatureUnit.CELSIUS)
        self.assertEqual(result.humidity, 65.0)
    
    def test_dump_report(self):
        """Test serializing a Report model."""
        report = Report(
            id=self.test_id,
            location_id=self.location_id,
            timestamp=self.timestamp,
            source="Weather Station",
            temperature_current=22.5,
            temperature_unit=TemperatureUnit.CELSIUS,
            humidity=65.0
        )
        
        schema = ReportSchema()
        result = schema.dump(report)
        
        self.assertEqual(result["id"], str(self.test_id))
        self.assertEqual(result["location_id"], str(self.location_id))
        self.assertIn(self.timestamp.isoformat()[:19], result["timestamp"])  # Check timestamp format
        self.assertEqual(result["source"], "Weather Station")
        self.assertEqual(result["temperature"], 22.5)  # Check data_key renamed from temperature_current
        self.assertEqual(result["temperature_unit"], "celsius")
        self.assertEqual(result["humidity"], 65.0)


class TestReportConditionSchema(unittest.TestCase):
    """Test cases for the ReportConditionSchema."""

    def setUp(self):
        """Set up test data."""
        self.test_id = uuid4()
        self.report_id = uuid4()
        self.condition_id = uuid4()
        self.valid_data = {
            "report_id": str(self.report_id),
            "condition_id": str(self.condition_id)
        }
        
    def test_load_valid_data(self):
        """Test loading valid data into a ReportCondition model."""
        schema = ReportConditionSchema()
        result = schema.load(self.valid_data)
        
        self.assertIsInstance(result, ReportCondition)
        self.assertEqual(result.report_id, self.report_id)
        self.assertEqual(result.condition_id, self.condition_id)
    
    def test_dump_report_condition(self):
        """Test serializing a ReportCondition model."""
        report_condition = ReportCondition(
            id=self.test_id,
            report_id=self.report_id,
            condition_id=self.condition_id
        )
        
        schema = ReportConditionSchema()
        result = schema.dump(report_condition)
        
        self.assertEqual(result["id"], str(self.test_id))
        self.assertEqual(result["report_id"], str(self.report_id))
        self.assertEqual(result["condition_id"], str(self.condition_id))


if __name__ == "__main__":
    unittest.main() 