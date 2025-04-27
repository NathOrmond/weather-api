from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
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


@dataclass
class Condition:
    name: str
    type: ConditionType
    intensity: IntensityLevel
    id: UUID = field(default_factory=uuid4)


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


@dataclass
class ReportCondition:
    report_id: UUID
    condition_id: UUID
    id: UUID = field(default_factory=uuid4) 