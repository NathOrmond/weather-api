import logging
from typing import Dict, Tuple, Any, Union

from api.services.weather_service import WeatherService

logger = logging.getLogger(__name__)

def add_weather_report(body: Dict) -> Tuple[Dict[str, Any], int]:
    """
    Add a new weather report for a city.
    
    Args:
        body: The request body containing the weather report data
        
    Returns:
        The created weather report as a dictionary and HTTP status code
        
    Raises:
        400: If validation fails
        404: If the city is not found
        500: For unexpected errors
    """
    logger.info(f"Received add_weather_report request: {body}")
    
    city_name = body.get("city")
    temperature = body.get("temperature")
    timestamp_str = body.get("timestamp")
    condition_name = body.get("condition")
    humidity = body.get("humidity", 0.0)
    
    result, error_msg = WeatherService.add_weather_report(
        city_name=city_name,
        temperature=temperature,
        timestamp_str=timestamp_str,
        condition_name=condition_name,
        humidity=humidity
    )
    
    if error_msg:
        if "City" in error_msg:
            return {"error": "Resource not found", "detail": error_msg}, 404
        elif "Invalid timestamp" in error_msg:
            return {"error": "Validation error", "detail": {"timestamp": ["Invalid timestamp format"]}}, 400
        else:
            return {"error": "Internal server error", "detail": error_msg}, 500
    
    return result, 201

def get_all_city_summaries() -> Tuple[Dict[str, Any], int]:
    """
    Retrieve a summary of all cities with their latest weather conditions.
    
    Returns:
        A dictionary containing a list of city summaries and HTTP status code
        
    Raises:
        500: For unexpected errors
    """
    logger.info("Received get_all_city_summaries request")
    
    result, error_msg = WeatherService.get_all_city_summaries()
    
    if error_msg:
        return {"error": "Internal server error", "detail": error_msg}, 500
    
    return result, 200

def get_city_weather(city: str) -> Tuple[Dict[str, Any], int]:
    """
    Get the latest weather report for a specific city.
    
    Args:
        city: The name of the city
        
    Returns:
        The latest weather report for the city and HTTP status code
        
    Raises:
        404: If the city or weather report is not found
        500: For unexpected errors
    """
    logger.info(f"Received get_city_weather request for city: {city}")
    
    result, error_msg = WeatherService.get_city_weather(city_name=city)
    
    if error_msg:
        if "City" in error_msg or "No weather reports" in error_msg:
            return {"error": "Resource not found", "detail": error_msg}, 404
        else:
            return {"error": "Internal server error", "detail": error_msg}, 500
    
    return result, 200

def update_city_weather(city: str, body: Dict) -> Tuple[Dict[str, Any], int]:
    """
    Update the latest weather report for a specific city.
    
    Args:
        city: The name of the city
        body: The request body containing the updated weather data
        
    Returns:
        The updated weather report and HTTP status code
        
    Raises:
        400: If validation fails
        404: If the city or weather report is not found
        500: For unexpected errors
    """
    logger.info(f"Received update_city_weather request for city: {city} with data: {body}")
    
    result, error_msg = WeatherService.update_city_weather(
        city_name=city,
        updates=body
    )
    
    if error_msg:
        if "City" in error_msg or "No weather reports" in error_msg:
            return {"error": "Resource not found", "detail": error_msg}, 404
        elif "Invalid timestamp" in error_msg:
            return {"error": "Validation error", "detail": {"timestamp": ["Invalid timestamp format"]}}, 400
        else:
            return {"error": "Internal server error", "detail": error_msg}, 500
    
    return result, 200

def delete_city_weather(city: str) -> Tuple[Union[Dict[str, Any], str], int]:
    """
    Delete all weather reports for a specific city.
    
    Args:
        city: The name of the city
        
    Returns:
        Empty response with 204 status code
        
    Raises:
        404: If the city or any reports for the city are not found
        500: For unexpected errors
    """
    logger.info(f"Received delete_city_weather request for city: {city}")
    
    success, error_msg = WeatherService.delete_city_weather(city_name=city)
    
    if not success:
        if error_msg and ("City" in error_msg or "No weather reports" in error_msg):
            return {"error": "Resource not found", "detail": error_msg}, 404
        else:
            return {"error": "Internal server error", "detail": error_msg}, 500
    
    return "", 204 