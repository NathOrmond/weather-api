import datetime

def add_weather_report(body):
    """Add a new weather report for a city"""
    # Implementation placeholder
    # In a real app, you would save this to a database
    timestamp = body.get('timestamp') or datetime.datetime.now().isoformat()
    return {
        "id": 1,  # In a real system, this would be generated
        "city": body["city"],
        "temperature": body["temperature"],
        "condition": body["condition"],
        "timestamp": timestamp
    }, 201

def get_city_weather(city):
    """Get the latest weather for a city"""
    # Implementation placeholder
    # In a real app, you would query the database
    
    # For demo purposes, return mock data for "London" or 404 for any other city
    if city.lower() == "london":
        return {
            "id": 1,
            "city": "London",
            "temperature": 18.5,
            "condition": "Cloudy",
            "timestamp": "2025-04-26T12:00:00Z"
        }, 200
    
    return {"error": "Resource not found", "detail": f"No weather data found for {city}"}, 404

def get_all_city_summaries():
    """Get summaries for all cities"""
    # Implementation placeholder
    # In a real app, you would query the database for all cities' latest reports
    
    return {
        "cities": [
            {
                "city": "London",
                "temperature": 18.5,
                "condition": "Cloudy",
                "timestamp": "2025-04-26T12:00:00Z"
            },
            {
                "city": "Paris",
                "temperature": 22.0,
                "condition": "Sunny",
                "timestamp": "2025-04-26T11:30:00Z"
            }
        ]
    }, 200

def update_city_weather(city, body):
    """Update the weather for a city"""
    # Implementation placeholder
    # In a real app, you would update the database
    
    # For demo purposes, return success for "London" or 404 for any other city
    if city.lower() == "london":
        timestamp = body.get('timestamp') or datetime.datetime.now().isoformat()
        return {
            "id": 1,
            "city": city,
            "temperature": body["temperature"],
            "condition": body["condition"],
            "timestamp": timestamp
        }, 200
    
    return {"error": "Resource not found", "detail": f"No weather data found for {city}"}, 404

def delete_city_weather(city):
    """Delete all weather reports for a city"""
    # Implementation placeholder
    # In a real app, you would delete from the database
    
    # For demo purposes, return success for "London" or 404 for any other city
    if city.lower() == "london":
        return "", 204
    
    return {"error": "Resource not found", "detail": f"No weather data found for {city}"}, 404 