import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from uuid import UUID

from api.models.domain import (
    Report, TemperatureUnit, Location, City, Condition, 
    ConditionType, IntensityLevel, ReportCondition
)
from api.repositories.memory_repository import (
    city_repository, location_repository, report_repository, 
    condition_repository, report_condition_repository
)

logger = logging.getLogger(__name__)

class WeatherService:
    """Service class for handling weather-related business logic."""
    
    @staticmethod
    def add_weather_report(city_name: str, temperature: float, 
                           timestamp_str: Optional[str] = None, 
                           condition_name: Optional[str] = None,
                           humidity: float = 0.0) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Add a new weather report for a city.
        
        Args:
            city_name: The name of the city
            temperature: The temperature value
            timestamp_str: ISO-formatted timestamp string (optional)
            condition_name: Weather condition name (optional)
            humidity: Humidity percentage (optional)
            
        Returns:
            Tuple of (report_dict, error_message)
            If successful, report_dict contains the created report and error_message is None
            If failed, report_dict is None and error_message contains the error details
        """
        try:
            city = city_repository.find_by_name(city_name)
            if not city:
                logger.info(f"City '{city_name}' not found, creating it")
                # TODO: Use a real repo of locations for lat, lng, elevation, timezone
                new_location = Location(
                    name=f"{city_name} Area",
                    latitude=0.0,  
                    longitude=0.0,
                    elevation=0.0,
                    timezone="UTC"  
                )
                stored_location = location_repository.add(new_location)
                # TODO: Use a real repo of countries for country
                new_city = City(
                    name=city_name,
                    country="Unknown",  
                    location_id=stored_location.id
                )
                city = city_repository.add(new_city)
                logger.info(f"Created new city '{city_name}' with id {city.id}")
            try:
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = datetime.utcnow()  
            except ValueError as e:
                logger.error(f"Invalid timestamp format: {e}")
                return None, "Invalid timestamp format"
            new_report = Report(
                location_id=city.location_id,
                timestamp=timestamp,
                source="API",
                temperature_current=temperature,
                temperature_unit=TemperatureUnit.CELSIUS,
                humidity=humidity
            )
            created_report = report_repository.add(new_report)
            if condition_name:
                error_msg = WeatherService._add_condition_to_report(condition_name, created_report.id)
                if error_msg:
                    logger.warning(error_msg)
                    # Continue without adding condition, but log the warning
            result = created_report.to_dict()
            result["city"] = city_name
            if condition_name:
                result["condition"] = condition_name
            return result, None
            
        except Exception as e:
            logger.exception(f"Unexpected error in add_weather_report: {e}")
            return None, f"Internal error: {str(e)}"
    
    @staticmethod
    def get_all_city_summaries() -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Retrieve a summary of all cities with their latest weather conditions.
        
        Returns:
            Tuple of (summaries_dict, error_message)
            If successful, summaries_dict contains the city summaries and error_message is None
            If failed, summaries_dict is None and error_message contains the error details
        """
        try:
            cities = city_repository.get_all()
            city_summaries = []
            
            for city in cities:
                # Get the latest report for this city's location
                latest_reports = report_repository.find_by_location_id(city.location_id, latest_only=True)
                
                if latest_reports:
                    latest_report = latest_reports[0]
                    
                    # Get condition for report
                    condition_name = WeatherService._get_condition_for_report(latest_report.id)
                    
                    # Build city summary
                    city_summary = {
                        "city": city.name,
                        "temperature": latest_report.temperature_current,
                        "condition": condition_name,
                        "timestamp": latest_report.timestamp.isoformat(),
                        "humidity": latest_report.humidity
                    }
                    city_summaries.append(city_summary)
            
            return {"cities": city_summaries}, None
            
        except Exception as e:
            logger.exception(f"Unexpected error in get_all_city_summaries: {e}")
            return None, f"Internal error: {str(e)}"
    
    @staticmethod
    def get_city_weather(city_name: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Get the latest weather report for a specific city.
        
        Args:
            city_name: The name of the city
            
        Returns:
            Tuple of (report_dict, error_message)
            If successful, report_dict contains the latest report and error_message is None
            If failed, report_dict is None and error_message contains the error details
        """
        try:
            # Find the city
            city = city_repository.find_by_name(city_name)
            if not city:
                logger.warning(f"City not found: {city_name}")
                return None, f"City '{city_name}' not found"
            
            # Get the latest report for this city's location
            latest_reports = report_repository.find_by_location_id(city.location_id, latest_only=True)
            
            if not latest_reports:
                logger.warning(f"No weather reports found for city: {city_name}")
                return None, f"No weather reports found for city '{city_name}'"
            
            latest_report = latest_reports[0]
            
            # Get condition for report
            condition_name = WeatherService._get_condition_for_report(latest_report.id)
            
            # Prepare response
            result = latest_report.to_dict()
            
            # Add city name and condition for API compatibility
            result["city"] = city_name
            if condition_name:
                result["condition"] = condition_name
                
            return result, None
            
        except Exception as e:
            logger.exception(f"Unexpected error in get_city_weather: {e}")
            return None, f"Internal error: {str(e)}"
    
    @staticmethod
    def update_city_weather(city_name: str, updates: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Update the latest weather report for a specific city.
        
        Args:
            city_name: The name of the city
            updates: Dictionary of fields to update
            
        Returns:
            Tuple of (updated_report_dict, error_message)
            If successful, updated_report_dict contains the updated report and error_message is None
            If failed, updated_report_dict is None and error_message contains the error details
        """
        try:
            # Find the city
            city = city_repository.find_by_name(city_name)
            if not city:
                logger.warning(f"City not found: {city_name}")
                return None, f"City '{city_name}' not found"
            
            # Get the latest report for this city's location
            latest_reports = report_repository.find_by_location_id(city.location_id, latest_only=True)
            
            if not latest_reports:
                logger.warning(f"No weather reports found for city: {city_name}")
                return None, f"No weather reports found for city '{city_name}'"
            
            latest_report = latest_reports[0]
            
            # Update timestamp if provided
            if "timestamp" in updates:
                try:
                    timestamp_str = updates["timestamp"]
                    if timestamp_str:
                        latest_report.timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except ValueError as e:
                    logger.error(f"Invalid timestamp format: {e}")
                    return None, "Invalid timestamp format"
            
            # Update temperature if provided
            if "temperature" in updates:
                latest_report.temperature_current = updates["temperature"]
            
            # Update humidity if provided
            if "humidity" in updates:
                latest_report.humidity = updates["humidity"]
            
            # Update report in repository
            updated_report = report_repository.update(latest_report)
            
            # Update condition if provided
            condition_name = updates.get("condition")
            if condition_name:
                # Remove existing conditions
                WeatherService._remove_conditions_for_report(updated_report.id)
                
                # Add new condition
                error_msg = WeatherService._add_condition_to_report(condition_name, updated_report.id)
                if error_msg:
                    logger.warning(error_msg)
                    # Continue without adding condition, but log the warning
            
            # Prepare response
            result = updated_report.to_dict()
            
            # Add city name and condition for API compatibility
            result["city"] = city_name
            if condition_name:
                result["condition"] = condition_name
                
            return result, None
            
        except Exception as e:
            logger.exception(f"Unexpected error in update_city_weather: {e}")
            return None, f"Internal error: {str(e)}"
    
    @staticmethod
    def delete_city_weather(city_name: str) -> Tuple[bool, Optional[str]]:
        """
        Delete all weather reports for a specific city.
        
        Args:
            city_name: The name of the city
            
        Returns:
            Tuple of (success, error_message)
            If successful, success is True and error_message is None
            If failed, success is False and error_message contains the error details
        """
        try:
            # Find the city
            city = city_repository.find_by_name(city_name)
            if not city:
                logger.warning(f"City not found: {city_name}")
                return False, f"City '{city_name}' not found"
            
            # Get all reports for this city's location
            reports = report_repository.find_by_location_id(city.location_id)
            
            if not reports:
                logger.warning(f"No weather reports found for city: {city_name}")
                return False, f"No weather reports found for city '{city_name}'"
            
            # Delete all reports and their associated conditions
            for report in reports:
                # Delete associated report conditions
                WeatherService._remove_conditions_for_report(report.id)
                
                # Delete the report
                report_repository.delete(report.id)
            
            return True, None
            
        except Exception as e:
            logger.exception(f"Unexpected error in delete_city_weather: {e}")
            return False, f"Internal error: {str(e)}"
    
    # --- Helper Methods ---
    
    @staticmethod
    def _add_condition_to_report(condition_name: str, report_id: UUID) -> Optional[str]:
        """
        Add a condition to a report.
        
        Args:
            condition_name: The name of the condition
            report_id: The ID of the report
            
        Returns:
            None if successful, error message if failed
        """
        try:
            # Map the condition name to ConditionType enum
            try:
                condition_type = ConditionType[condition_name.upper()]
            except KeyError:
                return f"Invalid condition type: {condition_name}"
            
            # Try to find existing condition or create new one
            condition = condition_repository.find_by_name(condition_name)
            if not condition:
                condition = Condition(
                    name=condition_name,
                    type=condition_type,
                    intensity=IntensityLevel.MODERATE  # Default intensity
                )
                condition = condition_repository.add(condition)
            
            # Create report-condition link
            report_condition = ReportCondition(
                report_id=report_id,
                condition_id=condition.id
            )
            report_condition_repository.add(report_condition)
            
            return None
            
        except Exception as e:
            return f"Error adding condition: {str(e)}"
    
    @staticmethod
    def _get_condition_for_report(report_id: UUID) -> Optional[str]:
        """
        Get the condition name for a report.
        
        Args:
            report_id: The ID of the report
            
        Returns:
            The condition name or None if no condition exists
        """
        report_conditions = report_condition_repository.find_by_report_id(report_id)
        if report_conditions:
            condition = condition_repository.get_by_id(report_conditions[0].condition_id)
            if condition:
                return condition.name
        return None
    
    @staticmethod
    def _remove_conditions_for_report(report_id: UUID) -> None:
        """
        Remove all conditions for a report.
        
        Args:
            report_id: The ID of the report
        """
        report_conditions = report_condition_repository.find_by_report_id(report_id)
        for rc in report_conditions:
            report_condition_repository.delete(rc.id) 