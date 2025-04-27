from datetime import datetime
import logging

# Import domain models and repository instances
from api.models.domain import Location, City, Condition, Report, ReportCondition, ConditionType, IntensityLevel, TemperatureUnit
from .memory_repository import (
    location_repository,
    city_repository,
    condition_repository,
    report_repository,
    report_condition_repository
)

logger = logging.getLogger(__name__)

def seed_data():
    """Populates the in-memory repositories with sample data."""
    logger.info("Seeding initial data into in-memory repositories...")

    # Clear existing data first (optional, useful for restarts)
    location_repository.clear()
    city_repository.clear()
    condition_repository.clear()
    report_repository.clear()
    report_condition_repository.clear()

    try:
        # Create Locations
        loc_london = Location(name="London Centre", latitude=51.5074, longitude=-0.1278, elevation=11.0, timezone="Europe/London")
        loc_tokyo = Location(name="Tokyo Station", latitude=35.6812, longitude=139.7671, elevation=5.0, timezone="Asia/Tokyo")
        location_repository.add(loc_london)
        location_repository.add(loc_tokyo)

        # Create Cities
        city_london = City(name="London", country="United Kingdom", location_id=loc_london.id)
        city_tokyo = City(name="Tokyo", country="Japan", location_id=loc_tokyo.id)
        city_repository.add(city_london)
        city_repository.add(city_tokyo)

        # Create Conditions
        cond_sunny = Condition(name="Sunny", type=ConditionType.SUNNY, intensity=IntensityLevel.MODERATE)
        cond_cloudy = Condition(name="Cloudy", type=ConditionType.CLOUDY, intensity=IntensityLevel.MODERATE)
        cond_light_rain = Condition(name="Light Rain", type=ConditionType.RAINY, intensity=IntensityLevel.LIGHT)
        condition_repository.add(cond_sunny)
        condition_repository.add(cond_cloudy)
        condition_repository.add(cond_light_rain)

        # Create Reports
        report_london_1 = Report(
            location_id=loc_london.id, 
            timestamp=datetime(2025, 4, 27, 10, 0, 0), 
            source="Local Sensor",
            temperature_current=14.5, 
            temperature_unit=TemperatureUnit.CELSIUS, 
            humidity=65.0
        )
        report_london_2 = Report(
            location_id=loc_london.id, 
            timestamp=datetime(2025, 4, 27, 11, 0, 0), 
            source="Local Sensor",
            temperature_current=15.1, 
            temperature_unit=TemperatureUnit.CELSIUS, 
            humidity=62.0
        )
        report_tokyo_1 = Report(
            location_id=loc_tokyo.id, 
            timestamp=datetime(2025, 4, 27, 18, 0, 0), 
            source="JMA",
            temperature_current=22.0, 
            temperature_unit=TemperatureUnit.CELSIUS, 
            humidity=75.0
        )
        report_repository.add(report_london_1)
        report_repository.add(report_london_2)
        report_repository.add(report_tokyo_1)

        # Create Report-Condition links
        rc_london_1_cloud = ReportCondition(report_id=report_london_1.id, condition_id=cond_cloudy.id)
        rc_london_2_sun = ReportCondition(report_id=report_london_2.id, condition_id=cond_sunny.id)
        rc_tokyo_1_rain = ReportCondition(report_id=report_tokyo_1.id, condition_id=cond_light_rain.id)
        report_condition_repository.add(rc_london_1_cloud)
        report_condition_repository.add(rc_london_2_sun)
        report_condition_repository.add(rc_tokyo_1_rain)

        logger.info("Finished seeding data.")
        logger.info(f"Locations: {len(location_repository.get_all())}, Cities: {len(city_repository.get_all())}, "
                    f"Conditions: {len(condition_repository.get_all())}, Reports: {len(report_repository.get_all())}, "
                    f"ReportConditions: {len(report_condition_repository.get_all())}")

    except Exception as e:
        logger.error(f"Error during seeding: {e}", exc_info=True) 