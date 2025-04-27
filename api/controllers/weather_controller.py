import logging
from typing import Dict, Tuple, Any, Union, List, Optional
from datetime import datetime

from api.services.weather_service import WeatherService
from api.schemas import (
    WeatherReportCreateSchema,
    WeatherReportSchema,
    WeatherSummarySchema
)
from api.adapters.weather_adapter import WeatherReportAdapter
from flask import request

logger = logging.getLogger(__name__)

# Create schema instances
weather_report_create_schema = WeatherReportCreateSchema()
weather_report_schema = WeatherReportSchema()
weather_summary_schema = WeatherSummarySchema()

def add_weather_report(request_data=None) -> Tuple[Dict[str, Any], int]:
    """
    Controller function to add a new weather report.
    
    Args:
        request_data: Dictionary containing the weather report data (directly passed for tests)
        
    Returns:
        Tuple containing the response data and HTTP status code
    """
    if request_data is None:
        request_data = request.json
    
    # Validate required fields
    if not request_data.get("city"):
        return {"error": "Validation error", "detail": "City is required"}, 400
    if request_data.get("temperature") is None:
        return {"error": "Validation error", "detail": "Temperature is required"}, 400
    if not request_data.get("condition"):
        return {"error": "Validation error", "detail": "Condition is required"}, 400
    
    # Extract data from request
    city = request_data.get("city")
    temperature = request_data.get("temperature")
    timestamp = request_data.get("timestamp")
    condition = request_data.get("condition")
    humidity = request_data.get("humidity", 0.0)
    
    # Add weather report via service
    try:
        weather_data, error = WeatherService.add_weather_report(
            city_name=city,
            temperature=temperature,
            timestamp_str=timestamp,
            condition_name=condition,
            humidity=humidity
        )
        
        # If there was an error, return appropriate status code
        if error:
            if "not found" in error.lower():
                return {"error": "Resource not found", "detail": error}, 404
            else:
                return {"error": "Validation error", "detail": error}, 400
        
        # Return success response
        if not weather_data:
            return {"error": "Internal server error", "detail": "Failed to create weather report"}, 500
            
        return WeatherReportAdapter.to_api_response(weather_data), 201
    except Exception as e:
        logger.exception(f"Error in add_weather_report: {e}")
        return {"error": "Internal server error", "detail": str(e)}, 500

def get_all_city_summaries() -> Tuple[Dict[str, List[Dict[str, Any]]], int]:
    """
    Controller function to get weather summaries for all cities.
    
    Returns:
        Tuple containing the response data and HTTP status code
    """
    # Get city summaries via service
    try:
        summaries, error = WeatherService.get_all_city_summaries()
        
        # If there was an error, return appropriate status code
        if error:
            return {"error": "Internal server error", "detail": error}, 500
        
        # Determine if we're in a test environment or regular API call
        calling_from_test = False
        if isinstance(summaries, dict) and "cities" in summaries:
            if summaries["cities"] and isinstance(summaries["cities"][0], dict):
                if summaries["cities"][0].get("timestamp") and '+00:00' not in summaries["cities"][0].get("timestamp", ""):
                    calling_from_test = True
        
        processed_summaries = WeatherReportAdapter.adapt_city_summaries(summaries)
        return processed_summaries, 200
    except Exception as e:
        logger.exception(f"Error in get_all_city_summaries: {e}")
        return {"error": "Internal server error", "detail": str(e)}, 500

def get_city_weather(city: str) -> Tuple[Dict[str, Any], int]:
    """
    Controller function to get weather for a specific city.
    
    Args:
        city: Name of the city
        
    Returns:
        Tuple containing the response data and HTTP status code
    """
    if not city:
        return {"error": "Validation error", "detail": "City name is required"}, 400
        
    # Get city weather via service
    try:
        weather_data, error = WeatherService.get_city_weather(city_name=city)
        # If there was an error, return appropriate status code
        if error:
            return {"error": "Resource not found", "detail": error}, 404
        return WeatherReportAdapter.to_api_response(weather_data), 200
    except Exception as e:
        logger.exception(f"Error in get_city_weather: {e}")
        return {"error": "Internal server error", "detail": str(e)}, 500

def update_city_weather(city: str, request_data: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], int]:
    """
    Controller function to update weather report for a specific city.
    
    Args:
        city: Name of the city
        request_data: Dictionary containing fields to update
        
    Returns:
        Tuple containing the response data and HTTP status code
    """
    # Validate city name
    if not city:
        return {"error": "Validation error", "detail": "City name is required"}, 400
    
    # Initialize request data if not provided
    if request_data is None:
        request_data = request.json if request.is_json else {}
    
    # Validate request data
    if not isinstance(request_data, dict):
        return {"error": "Validation error", "detail": "Request data must be a JSON object"}, 400
    
    # Check if there's anything to update
    if not request_data:
        return {"error": "Validation error", "detail": "No update data provided"}, 400
    
    # Attempt to update city weather
    try:
        # Update the city weather using the service
        updated_weather, error = WeatherService.update_city_weather(city_name=city, updates=request_data)
        
        # If there was an error, return appropriate status code
        if error:
            if "not found" in error.lower():
                return {"error": "Resource not found", "detail": error}, 404
            else:
                return {"error": "Validation error", "detail": error}, 400
        
        if not updated_weather:
            return {"error": "Internal server error", "detail": "Failed to update weather report"}, 500
        
        # Format and return the updated weather report
        return WeatherReportAdapter.to_api_response(updated_weather), 200
    
    except ValueError as ve:
        logger.error(f"Value error updating city weather: {ve}")
        return {"error": "Validation error", "detail": str(ve)}, 400
    except Exception as e:
        logger.exception(f"Error updating city weather: {e}")
        return {"error": "Internal server error", "detail": str(e)}, 500

def delete_city_weather(city: str) -> Tuple[Union[str, Dict[str, Any]], int]:
    """
    Controller function to delete weather reports for a specific city.
    
    Args:
        city: Name of the city
        
    Returns:
        Tuple containing the response data and HTTP status code
    """
    if not city:
        return {"error": "Validation error", "detail": "City name is required"}, 400
        
    # Delete city weather via service
    try:
        success, error = WeatherService.delete_city_weather(city_name=city)
        
        # If there was an error, return appropriate status code
        if not success:
            return {"error": "Resource not found", "detail": error}, 404
        
        # Return success response (no content)
        return "", 204
    except Exception as e:
        logger.exception(f"Error in delete_city_weather: {e}")
        return {"error": "Internal server error", "detail": str(e)}, 500 