from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4


class ConditionType(Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    FOGGY = "foggy"
    WINDY = "windy"
    STORMY = "stormy"


class IntensityLevel(Enum):
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    SEVERE = "severe"


class TemperatureUnit(Enum):
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"
    KELVIN = "kelvin"


@dataclass
class Location:
    name: str
    latitude: float
    longitude: float
    elevation: float
    timezone: str
    id: UUID = field(default_factory=uuid4)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the Location object to a dictionary for serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "elevation": self.elevation,
            "timezone": self.timezone
        }


@dataclass
class City:
    name: str
    country: str
    location_id: UUID
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        # For backward compatibility with seed data that passes Location object
        if hasattr(self, 'location') and self.location:
            self.location_id = self.location.id
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert the City object to a dictionary for serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "country": self.country,
            "location_id": str(self.location_id)
        }


@dataclass
class Condition:
    name: str
    type: ConditionType
    intensity: IntensityLevel
    id: UUID = field(default_factory=uuid4)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the Condition object to a dictionary for serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.type.value,
            "intensity": self.intensity.value
        }


@dataclass
class Report:
    location_id: UUID
    timestamp: datetime
    source: str
    temperature_current: float
    temperature_unit: TemperatureUnit
    humidity: float
    id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        # For backward compatibility with seed data that passes Location object
        if hasattr(self, 'location') and self.location:
            self.location_id = self.location.id
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert the Report object to a dictionary for serialization."""
        return {
            "id": str(self.id),
            "location_id": str(self.location_id),
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "temperature": self.temperature_current,
            "temperature_unit": self.temperature_unit.value,
            "humidity": self.humidity
        }


@dataclass
class ReportCondition:
    report_id: UUID
    condition_id: UUID
    id: UUID = field(default_factory=uuid4)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the ReportCondition object to a dictionary for serialization."""
        return {
            "id": str(self.id),
            "report_id": str(self.report_id),
            "condition_id": str(self.condition_id)
        } 