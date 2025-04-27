# Technical Specification: In-Memory Data Layer and Seeding

## 1. Introduction

This document outlines the design and implementation of an in-memory data storage layer for the Weather API application. This layer will serve as a temporary persistence mechanism during development, allowing controllers and services to interact with domain model entities (`Location`, `City`, `Condition`, `Report`, `ReportCondition`) without requiring a database setup. It is designed to be easily replaceable with a database-backed persistence layer in the future.

## 2. Objectives

-   Provide a simple, in-memory storage solution for the defined domain entities.
-   Implement the Repository pattern to abstract data access logic.
-   Define clear interfaces for interacting with the data store (CRUD operations).
-   Include a mechanism for seeding the in-memory store with initial sample data on application startup.
-   Ensure the design facilitates future migration to a persistent database (e.g., PostgreSQL, SQLite).

## 3. Design: Repository Pattern

The Repository pattern will be used to decouple the application's business logic (controllers/services) from the data storage mechanism.

-   **Base Repository (Optional but Recommended):** An abstract base class or protocol could define common methods (`add`, `get_by_id`, `get_all`, `update`, `delete`), but for simplicity in this initial phase, we can define concrete methods directly in the in-memory implementations.
-   **Concrete In-Memory Repositories:** Separate classes will be created for each primary domain entity (`Location`, `City`, `Condition`, `Report`). These repositories will manage their respective entities using Python dictionaries, where the keys are the entity UUIDs and the values are the entity objects.
-   **Data Storage:** Each repository instance will hold its data in a class-level or instance-level dictionary (e.g., `self._data: Dict[UUID, YourEntity] = {}`).

## 4. Implementation Details

### 4.1. Domain Models (`api/models/domain.py` or similar)

Use the provided dataclasses (`Location`, `City`, `Condition`, `Report`, `ReportCondition`) as the core domain entities. Place this code in a suitable location, e.g., `api/models/domain.py`.

*(Include the dataclass code provided by the user here if desired, or reference its location)*

### 4.2. In-Memory Repositories (`api/repositories/memory_repository.py`)

Create a new file, e.g., `api/repositories/memory_repository.py`. Implement repository classes for each entity.

```python
# File: api/repositories/memory_repository.py

from uuid import UUID, uuid4
from typing import Dict, List, Optional, TypeVar, Generic
from copy import deepcopy
import logging

# Import your domain models (adjust path as necessary)
from api.models.domain import Location, City, Condition, Report, ReportCondition

logger = logging.getLogger(__name__)

# Generic Type Variable for entities
T = TypeVar('T')

class InMemoryRepository(Generic[T]):
    """
    Generic base for simple in-memory storage using a dictionary.
    Assumes entities have an 'id' attribute of type UUID.
    """
    def __init__(self):
        self._data: Dict[UUID, T] = {}
        logger.debug(f"Initialized InMemoryRepository for type {self.__class__.__name__}")

    def add(self, entity: T) -> T:
        """Adds a new entity."""
        if not hasattr(entity, 'id') or not isinstance(getattr(entity, 'id'), UUID):
            raise ValueError("Entity must have a UUID 'id' attribute")
        if entity.id in self._data:
            raise ValueError(f"Duplicate ID: Entity with ID {entity.id} already exists.")
        # Store a deep copy to simulate database behavior (prevent modification by reference)
        self._data[entity.id] = deepcopy(entity)
        logger.debug(f"Added entity {entity.id} to {self.__class__.__name__}")
        return deepcopy(entity) # Return a copy

    def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Gets an entity by its ID."""
        entity = self._data.get(entity_id)
        logger.debug(f"Attempted get for ID {entity_id} in {self.__class__.__name__}. Found: {entity is not None}")
        # Return a deep copy to prevent modification by reference
        return deepcopy(entity) if entity else None

    def get_all(self) -> List[T]:
        """Gets all entities."""
        logger.debug(f"Retrieving all {len(self._data)} entities from {self.__class__.__name__}")
        # Return deep copies
        return [deepcopy(entity) for entity in self._data.values()]

    def update(self, entity: T) -> Optional[T]:
        """Updates an existing entity."""
        if not hasattr(entity, 'id') or not isinstance(getattr(entity, 'id'), UUID):
            raise ValueError("Entity must have a UUID 'id' attribute")
        if entity.id not in self._data:
             logger.warning(f"Attempted update for non-existent ID {entity.id} in {self.__class__.__name__}")
             return None
        # Store a deep copy
        self._data[entity.id] = deepcopy(entity)
        logger.debug(f"Updated entity {entity.id} in {self.__class__.__name__}")
        return deepcopy(entity) # Return a copy

    def delete(self, entity_id: UUID) -> bool:
        """Deletes an entity by its ID. Returns True if deleted, False otherwise."""
        if entity_id in self._data:
            del self._data[entity_id]
            logger.debug(f"Deleted entity {entity_id} from {self.__class__.__name__}")
            return True
        logger.warning(f"Attempted delete for non-existent ID {entity_id} in {self.__class__.__name__}")
        return False

    def clear(self):
        """Clears all data from the repository."""
        count = len(self._data)
        self._data.clear()
        logger.info(f"Cleared {count} items from {self.__class__.__name__}")

# --- Concrete Repository Implementations ---

class InMemoryLocationRepository(InMemoryRepository[Location]):
    # Add specific query methods if needed, e.g.:
    def find_by_name(self, name: str) -> Optional[Location]:
        for entity in self._data.values():
            if entity.name == name:
                return deepcopy(entity)
        return None

class InMemoryCityRepository(InMemoryRepository[City]):
    # Add specific query methods if needed, e.g.:
    def find_by_name(self, name: str) -> Optional[City]:
        for entity in self._data.values():
            if entity.name == name:
                return deepcopy(entity)
        return None

    def find_by_location_id(self, location_id: UUID) -> List[City]:
        return [deepcopy(c) for c in self._data.values() if c.location_id == location_id]


class InMemoryConditionRepository(InMemoryRepository[Condition]):
    # Add specific query methods if needed
    pass

class InMemoryReportRepository(InMemoryRepository[Report]):
    # Add specific query methods if needed, e.g.:
    def find_by_location_id(self, location_id: UUID, latest_only: bool = False) -> List[Report]:
        reports = [deepcopy(r) for r in self._data.values() if r.location_id == location_id]
        reports.sort(key=lambda r: r.timestamp, reverse=True)
        return reports[:1] if latest_only and reports else reports

# Note: ReportCondition might be managed differently, potentially directly
# within the Report or Condition repositories or via a dedicated service,
# depending on how relationships are handled. A simple repository is shown here.
class InMemoryReportConditionRepository(InMemoryRepository[ReportCondition]):
     def find_by_report_id(self, report_id: UUID) -> List[ReportCondition]:
        return [deepcopy(rc) for rc in self._data.values() if rc.report_id == report_id]

     def find_by_condition_id(self, condition_id: UUID) -> List[ReportCondition]:
        return [deepcopy(rc) for rc in self._data.values() if rc.condition_id == condition_id]

# --- Singleton Instances ---
# Create singleton instances to be used across the application
# This simulates a shared data store.
location_repository = InMemoryLocationRepository()
city_repository = InMemoryCityRepository()
condition_repository = InMemoryConditionRepository()
report_repository = InMemoryReportRepository()
report_condition_repository = InMemoryReportConditionRepository()

4.3. Seeding Mechanism (api/repositories/seed.py)Create a function to populate the repositories with initial data.# File: api/repositories/seed.py

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
        city_london = City(name="London", country="United Kingdom", location=loc_london)
        city_tokyo = City(name="Tokyo", country="Japan", location=loc_tokyo)
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
            location=loc_london, timestamp=datetime(2025, 4, 27, 10, 0, 0), source="Local Sensor",
            temperature_current=14.5, temperature_unit=TemperatureUnit.CELSIUS, humidity=65.0
        )
        report_london_2 = Report(
            location=loc_london, timestamp=datetime(2025, 4, 27, 11, 0, 0), source="Local Sensor",
            temperature_current=15.1, temperature_unit=TemperatureUnit.CELSIUS, humidity=62.0
        )
        report_tokyo_1 = Report(
            location=loc_tokyo, timestamp=datetime(2025, 4, 27, 18, 0, 0), source="JMA",
            temperature_current=22.0, temperature_unit=TemperatureUnit.CELSIUS, humidity=75.0
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


4.4. Application Initialization (app.py)Modify app.py to call the seed_data function once during application startup. This should happen after logging is configured but before the server starts accepting requests.# File: app.py (Additions/Modifications)

# ... (other imports) ...
from api.repositories.seed import seed_data # <<< Import seed function

# ... (Configuration Loading, Logging Setup) ...

# --- Initialize Connexion ---
# ... (Connexion setup as before) ...

# --- Access Flask App, Apply CORS, Add API Spec ---
# ... (As before) ...

# --- Register Custom Flask Blueprints/Routes ---
# ... (As before) ...

# --- Seed Initial Data ---
# Call this once after app setup but before running the server
# Optionally make this conditional based on environment (e.g., only in dev)
if env == 'development': # Or based on a specific env variable
    seed_data()
else:
    logger.info("Skipping data seeding in non-development environment.")


# --- Main execution block ---
if __name__ == '__main__':
    # ... (As before, calling uvicorn.run) ...

# --- WSGI Entry Point ---
# ... (As before) ...

5. Integration with Controllers/ServicesYour API controllers (e.g., api/controllers/weather_controller.py) will now import the repository instances and use their methods to interact with the data.Example (api/controllers/weather_controller.py excerpt):# File: api/controllers/weather_controller.py (Example Excerpt)

import logging
from uuid import UUID
# Import repository instances
from api.repositories.memory_repository import report_repository, city_repository # etc.
# Import domain models if needed for type conversion
from api.models.domain import Report # etc.

logger = logging.getLogger(__name__)

def add_weather_report(body): # 'body' comes from Connexion request body parsing
    """Adds a new weather report."""
    logger.info(f"Received request to add weather report: {body}")
    try:
        # 1. Find related entities (e.g., Location based on city name)
        #    This might involve calls to city_repository, location_repository
        #    (Logic depends on how your request body maps to domain models)

        # 2. Create the Report domain object from the request body 'body'
        #    (Need data validation and mapping logic here)
        #    Example (highly simplified):
        #    city_name = body.get('city')
        #    city = city_repository.find_by_name(city_name)
        #    if not city: return {"error": "City not found"}, 404
        #
        #    new_report = Report(
        #        location=city.location, # Assuming city object has location loaded
        #        timestamp=body.get('timestamp'), # Needs parsing from string to datetime
        #        source="API Input", # Or get from body
        #        temperature_current=body.get('temperature'),
        #        # ... map other fields ...
        #    )

        # 3. Add to repository
        #    created_report = report_repository.add(new_report)

        # 4. Return the created report (serialized) and 201 status
        #    return created_report.to_dict(), 201 # Use your model's to_dict()
        pass # Replace with actual implementation
    except ValueError as ve:
         logger.warning(f"Validation error adding report: {ve}")
         return {"error": "Validation Error", "detail": str(ve)}, 400
    except Exception as e:
        logger.error(f"Error adding weather report: {e}", exc_info=True)
        return {"error": "Internal Server Error"}, 500


def get_city_weather(city: str): # 'city' comes from path parameter
    """Gets the latest weather report for a specific city."""
    logger.info(f"Received request to get weather for city: {city}")
    try:
        # 1. Find city and its location
        #    city_obj = city_repository.find_by_name(city)
        #    if not city_obj: return {"error": "City not found"}, 404

        # 2. Find reports for that location
        #    reports = report_repository.find_by_location_id(city_obj.location_id, latest_only=True)
        #    if not reports: return {"error": "No weather report found for this city"}, 404

        # 3. Return the latest report (serialized)
        #    return reports[0].to_dict(), 200
        pass # Replace with actual implementation
    except Exception as e:
        logger.error(f"Error getting weather for city {city}: {e}", exc_info=True)
        return {"error": "Internal Server Error"}, 500

# Implement other controller functions (get_all_city_summaries, update, delete)
# using the appropriate repository methods.

6. Future ConsiderationsDatabase Migration: When ready, create new repository implementations (e.g., api/repositories/db_repository.py) that use an ORM like SQLAlchemy to interact with a database. These new repositories should implement the same methods as the in-memory ones.Dependency Injection: To easily swap repositories, consider using a dependency injection framework (like python-dependency-injector) or a simpler factory pattern to provide the correct repository instance (in-memory or database) to the controllers/services based on configuration. For now, directly importing the singleton instances is acceptable for simplicity.Error Handling: Implement more robust error handling and validation in controllers.Data Relationships: Refine how relationships (like ReportCondition) are managed. It might be better handled within the Report repository or a dedicated service layer.Concurrency: The current in-memory implementation is not thread-safe. If multiple requests modify data concurrently, issues could arise. This is less of a concern for simple development/testing but critical for production (where a database handles concurrency).7. Expected OutcomeA functional in-memory data layer allowing the API to perform