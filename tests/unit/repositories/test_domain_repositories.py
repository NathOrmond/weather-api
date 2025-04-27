import unittest
import uuid
from datetime import datetime, timedelta

from api.models.domain import (
    Location, City, Condition, Report, ReportCondition,
    ConditionType, IntensityLevel, TemperatureUnit
)
from api.repositories.memory_repository import (
    InMemoryLocationRepository,
    InMemoryCityRepository,
    InMemoryConditionRepository, 
    InMemoryReportRepository,
    InMemoryReportConditionRepository
)


class TestLocationRepository(unittest.TestCase):
    """Test the Location repository implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.repo = InMemoryLocationRepository()
        self.location1 = Location(
            name="Test Location 1",
            latitude=51.5074,
            longitude=-0.1278,
            elevation=10.0,
            timezone="Europe/London"
        )
        self.location2 = Location(
            name="Test Location 2",
            latitude=40.7128,
            longitude=-74.0060,
            elevation=5.0,
            timezone="America/New_York"
        )
    
    def test_find_by_name(self):
        """Test finding a location by name."""
        # Add locations
        self.repo.add(self.location1)
        self.repo.add(self.location2)
        
        # Find by name
        result = self.repo.find_by_name("Test Location 1")
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.location1.id)
        
        # Find non-existent location
        result = self.repo.find_by_name("Nonexistent Location")
        self.assertIsNone(result)


class TestCityRepository(unittest.TestCase):
    """Test the City repository implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.repo = InMemoryCityRepository()
        self.location_id1 = uuid.uuid4()
        self.location_id2 = uuid.uuid4()
        
        self.city1 = City(
            name="London",
            country="United Kingdom",
            location_id=self.location_id1
        )
        self.city2 = City(
            name="Manchester",
            country="United Kingdom",
            location_id=self.location_id1  # Same location as city1
        )
        self.city3 = City(
            name="New York",
            country="United States",
            location_id=self.location_id2
        )
    
    def test_find_by_name(self):
        """Test finding a city by name."""
        # Add cities
        self.repo.add(self.city1)
        self.repo.add(self.city2)
        self.repo.add(self.city3)
        
        # Find by name
        result = self.repo.find_by_name("London")
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.city1.id)
        
        # Find non-existent city
        result = self.repo.find_by_name("Nonexistent City")
        self.assertIsNone(result)
    
    def test_find_by_location_id(self):
        """Test finding cities by location ID."""
        # Add cities
        self.repo.add(self.city1)
        self.repo.add(self.city2)
        self.repo.add(self.city3)
        
        # Find by location ID
        results = self.repo.find_by_location_id(self.location_id1)
        self.assertEqual(len(results), 2)
        city_ids = {c.id for c in results}
        self.assertEqual(city_ids, {self.city1.id, self.city2.id})
        
        # Find by non-existent location ID
        results = self.repo.find_by_location_id(uuid.uuid4())
        self.assertEqual(len(results), 0)


class TestConditionRepository(unittest.TestCase):
    """Test the Condition repository implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.repo = InMemoryConditionRepository()
        self.condition1 = Condition(
            name="Sunny",
            type=ConditionType.SUNNY,
            intensity=IntensityLevel.MODERATE
        )
        self.condition2 = Condition(
            name="Heavy Rain",
            type=ConditionType.RAINY,
            intensity=IntensityLevel.HEAVY
        )
    
    def test_find_by_name(self):
        """Test finding a condition by name."""
        # Add conditions
        self.repo.add(self.condition1)
        self.repo.add(self.condition2)
        
        # Find by name
        result = self.repo.find_by_name("Sunny")
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.condition1.id)
        
        # Find non-existent condition
        result = self.repo.find_by_name("Nonexistent Condition")
        self.assertIsNone(result)


class TestReportRepository(unittest.TestCase):
    """Test the Report repository implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.repo = InMemoryReportRepository()
        self.location_id1 = uuid.uuid4()
        self.location_id2 = uuid.uuid4()
        
        now = datetime.now()
        
        self.report1 = Report(
            location_id=self.location_id1,
            timestamp=now - timedelta(hours=2),
            source="Test Source",
            temperature_current=20.0,
            temperature_unit=TemperatureUnit.CELSIUS,
            humidity=60.0
        )
        self.report2 = Report(
            location_id=self.location_id1,
            timestamp=now - timedelta(hours=1),
            source="Test Source",
            temperature_current=21.0,
            temperature_unit=TemperatureUnit.CELSIUS,
            humidity=65.0
        )
        self.report3 = Report(
            location_id=self.location_id2,
            timestamp=now,
            source="Test Source",
            temperature_current=15.0,
            temperature_unit=TemperatureUnit.CELSIUS,
            humidity=70.0
        )
    
    def test_find_by_location_id(self):
        """Test finding reports by location ID."""
        # Add reports
        self.repo.add(self.report1)
        self.repo.add(self.report2)
        self.repo.add(self.report3)
        
        # Find by location ID
        results = self.repo.find_by_location_id(self.location_id1)
        self.assertEqual(len(results), 2)
        report_ids = {r.id for r in results}
        self.assertEqual(report_ids, {self.report1.id, self.report2.id})
        
        # Verify sorted by timestamp (descending)
        self.assertEqual(results[0].id, self.report2.id)  # More recent first
        self.assertEqual(results[1].id, self.report1.id)
        
        # Test latest_only flag
        results = self.repo.find_by_location_id(self.location_id1, latest_only=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.report2.id)  # Most recent only
        
        # Find by non-existent location ID
        results = self.repo.find_by_location_id(uuid.uuid4())
        self.assertEqual(len(results), 0)


class TestReportConditionRepository(unittest.TestCase):
    """Test the ReportCondition repository implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.repo = InMemoryReportConditionRepository()
        self.report_id1 = uuid.uuid4()
        self.report_id2 = uuid.uuid4()
        self.condition_id1 = uuid.uuid4()
        self.condition_id2 = uuid.uuid4()
        
        self.rc1 = ReportCondition(
            report_id=self.report_id1,
            condition_id=self.condition_id1
        )
        self.rc2 = ReportCondition(
            report_id=self.report_id1,
            condition_id=self.condition_id2
        )
        self.rc3 = ReportCondition(
            report_id=self.report_id2,
            condition_id=self.condition_id1
        )
    
    def test_find_by_report_id(self):
        """Test finding report conditions by report ID."""
        # Add report conditions
        self.repo.add(self.rc1)
        self.repo.add(self.rc2)
        self.repo.add(self.rc3)
        
        # Find by report ID
        results = self.repo.find_by_report_id(self.report_id1)
        self.assertEqual(len(results), 2)
        rc_ids = {rc.id for rc in results}
        self.assertEqual(rc_ids, {self.rc1.id, self.rc2.id})
        
        # Find by non-existent report ID
        results = self.repo.find_by_report_id(uuid.uuid4())
        self.assertEqual(len(results), 0)
    
    def test_find_by_condition_id(self):
        """Test finding report conditions by condition ID."""
        # Add report conditions
        self.repo.add(self.rc1)
        self.repo.add(self.rc2)
        self.repo.add(self.rc3)
        
        # Find by condition ID
        results = self.repo.find_by_condition_id(self.condition_id1)
        self.assertEqual(len(results), 2)
        rc_ids = {rc.id for rc in results}
        self.assertEqual(rc_ids, {self.rc1.id, self.rc3.id})
        
        # Find by non-existent condition ID
        results = self.repo.find_by_condition_id(uuid.uuid4())
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main() 