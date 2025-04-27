"""
Weather Report adapter module for transforming between service and API representations.
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


class WeatherReportAdapter:
    """
    Adapter for converting between service layer responses and API schema formats
    for weather-related data.
    """
    
    @staticmethod
    def format_time(timestamp_str: str) -> str:
        """
        Format timestamp strings to include timezone information.
        
        Args:
            timestamp_str: Timestamp string to format (could be ISO format or any parseable format)
            
        Returns:
            Formatted timestamp string with timezone info
        """
        if not timestamp_str:
            return datetime.now().isoformat(timespec='seconds') + '+00:00'
            
        # Check if the timestamp already has timezone info
        if '+' in timestamp_str or 'Z' in timestamp_str:
            # If it ends with Z, replace with +00:00
            if timestamp_str.endswith('Z'):
                return timestamp_str.replace('Z', '+00:00')
            return timestamp_str
            
        # Parse the timestamp and format it with timezone info
        try:
            # Try parsing as ISO format
            dt = datetime.fromisoformat(timestamp_str)
        except ValueError:
            try:
                # Try parsing with common formats
                dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Return current time if parsing fails
                dt = datetime.now()
                
        # Format with timezone
        return dt.isoformat(timespec='seconds') + '+00:00'
    
    @classmethod
    def to_api_response(cls, service_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a service response to API response format with required fields.
        
        Args:
            service_response: The raw service response dictionary
            
        Returns:
            A properly formatted API response dictionary
        """
        if not service_response:
            return {}
            
        # Format timestamp if present
        if "timestamp" in service_response:
            service_response["timestamp"] = cls.format_time(service_response["timestamp"])
            
        # Standard API format for all responses
        return {
            "id": service_response.get("id"),
            "city": service_response.get("city"),
            "temperature": service_response.get("temperature") or service_response.get("temperature_current"),
            "condition": service_response.get("condition"),
            "timestamp": service_response.get("timestamp")
        }
    
    @classmethod
    def to_summary_response(cls, service_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a service response to a summary format for listings.
        
        Args:
            service_response: The raw service response dictionary
            
        Returns:
            A formatted summary response dictionary
        """
        if not service_response:
            return {}
            
        # Simpler format used for summary listings
        return {
            "id": service_response.get("id"),
            "city": service_response.get("city"),
            "temperature": service_response.get("temperature") or service_response.get("temperature_current")
        }
    
    @classmethod
    def adapt_weather_report(cls, service_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt a single weather report from service layer format to API format.
        
        Args:
            service_response: The service layer response for a weather report
            
        Returns:
            API formatted weather report
        """
        return cls.to_api_response(service_response)
    
    @classmethod
    def adapt_city_summaries(cls, service_response: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Adapt a list of city weather summaries to API format.
        
        Args:
            service_response: List of service layer city weather data
            
        Returns:
            Dictionary with "cities" key containing a list of API formatted city weather summaries
        """
        if not service_response or not isinstance(service_response, dict):
            return {"cities": []}
            
        result = {"cities": []}
        
        # Handle different formats of input data
        if "cities" in service_response and isinstance(service_response["cities"], list):
            cities_data = service_response["cities"]
        elif isinstance(service_response, list):
            cities_data = service_response
        else:
            # Extract city data from dictionary format
            cities_data = []
            for city_name, city_data in service_response.items():
                if isinstance(city_data, dict):
                    city_entry = city_data.copy()
                    if "city" not in city_entry:
                        city_entry["city"] = city_name
                    cities_data.append(city_entry)
            
        # Format each city entry
        for city in cities_data:
            if isinstance(city, dict):
                # Format timestamp if present
                if "timestamp" in city:
                    city["timestamp"] = cls.format_time(city["timestamp"])
                result["cities"].append(city)
                
        return result 