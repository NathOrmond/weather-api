# Auto-Creating Cities on POST Request

## Issue

When attempting to submit a weather report for a city that didn't already exist in the system, the API would return a 404 "City not found" error. This created a poor user experience as users had to first ensure the city existed before being able to submit weather data.

Example error when trying to submit a report for "Manchester" when it didn't exist in the database:

```
{
  "detail": "City 'Manchester' not found",
  "error": "Resource not found"
}
```

## Business Requirement

From a UX perspective, users submitting weather reports should be able to create reports for any city. The system should automatically create the city if it doesn't already exist.

## Solution

We modified the `add_weather_report` method in `api/services/weather_service.py` to auto-create the city (and a corresponding location) when a city is not found:

```python
@staticmethod
def add_weather_report(city_name: str, temperature: float, 
                       timestamp_str: Optional[str] = None, 
                       condition_name: Optional[str] = None,
                       humidity: float = 0.0) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Add a new weather report for a city.
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
            
        # ... rest of the method remains the same
```

The solution includes:

1. Logic to check if the city exists using `city_repository.find_by_name(city_name)`
2. If the city is not found, create a new Location with placeholder values
3. Create a new City referencing the created Location
4. Continue with creating the weather report using the newly created city

## Testing

We also updated the tests in `tests/unit/services/test_weather_service.py` to verify the new behavior:

1. Added a test case `test_add_weather_report_new_city` that verifies a new city is created when the city doesn't exist
2. Updated `test_add_weather_report_city_not_found` to reflect the changed behavior (this test was no longer valid since the city not found scenario now results in city creation)

Additionally, integration tests were updated to verify that a POST request for a nonexistent city successfully creates the city and adds a weather report.

## Verification

After implementing these changes, we tested the behavior by submitting a POST request to add a weather report for a city that didn't exist:

```bash
curl -X POST "http://localhost:5000/weather" \
  -H "Content-Type: application/json" \
  -d '{"city":"Manchester","temperature":21.5,"condition":"Sunny","timestamp":"2023-06-01T14:00:00Z"}'
```

The API now successfully creates the city and returns a 201 Created response with the created weather report:

```json
{
  "city": "Manchester",
  "condition": "Sunny",
  "humidity": 0.0,
  "id": "8839397b-deed-44ef-837f-90c1fcfdfcc2",
  "location_id": "a920231b-d4ef-4b78-925c-a4994b7c0a82",
  "source": "API",
  "temperature": 21.5,
  "temperature_unit": "celsius",
  "timestamp": "2023-06-01T14:00:00+00:00"
}
```

## Lessons Learned

1. **User Experience First**: Design APIs with user experience in mind, minimizing friction for common operations.

2. **Progressive Enhancement**: Start with simpler validations and add complexity as needed. In this case, we initially required cities to exist before allowing reports, but discovered this was an unnecessary restriction.

3. **Default Values**: When auto-creating related entities, provide sensible defaults (like setting country to "Unknown" and using UTC timezone) to maintain data integrity.

4. **Idempotent Behavior**: This implementation maintains idempotent behavior - submitting reports for the same city multiple times will only create the city once.

5. **Documentation**: Make sure to update API documentation to reflect that POST requests will now create cities if they don't exist, as this behavior might not be obvious to API consumers. 