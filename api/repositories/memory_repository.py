from uuid import UUID, uuid4
from typing import Dict, List, Optional, TypeVar, Generic
from copy import deepcopy
import logging
from datetime import timezone

# Import domain models
from api.models.domain import Location, City, Condition, Report, ReportCondition, ConditionType, IntensityLevel, TemperatureUnit

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
    def find_by_name(self, name: str) -> Optional[Condition]:
        for entity in self._data.values():
            if entity.name == name:
                return deepcopy(entity)
        return None

class InMemoryReportRepository(InMemoryRepository[Report]):
    # Add specific query methods if needed, e.g.:
    def find_by_location_id(self, location_id: UUID, latest_only: bool = False) -> List[Report]:
        reports = [deepcopy(r) for r in self._data.values() if r.location_id == location_id]
        
        # Make sure timestamps are comparable by ensuring consistent timezone info
        def get_timestamp_safe(report):
            # If the timestamp is timezone-aware, use it as is
            # If it's timezone-naive, assume UTC
            try:
                if report.timestamp.tzinfo is None:
                    return report.timestamp.replace(tzinfo=timezone.utc)
                return report.timestamp
            except Exception:
                # Fallback in case of any issues
                return report.timestamp
        
        # Sort using the safe timestamp access
        reports.sort(key=lambda r: get_timestamp_safe(r), reverse=True)
        return reports[:1] if latest_only and reports else reports

# Repository for managing ReportCondition relationships
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