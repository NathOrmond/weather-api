# UUID vs Integer Schema Mismatch in Weather API

## Issue

When making a GET request to `/weather/London`, the API returned a 500 Internal Server Error. The error occurred because there was a type mismatch between the domain model and the OpenAPI schema:

```
{
  "detail": "Internal error: integer is required for id field but got UUID string",
  "error": "Internal server error"
}
```

## Root Cause

The issue was caused by a mismatch between:

1. The **domain model** which used UUID objects for IDs:
   ```python
   # In domain.py
   @dataclass
   class Report:
       location_id: UUID
       # ...
       id: UUID = field(default_factory=uuid4)
   ```

2. The **OpenAPI schema** which defined the `id` field as an integer:
   ```yaml
   # In docs/openapi/components/schemas/weather.yaml
   WeatherReport:
     type: object
     properties:
       id:
         type: integer
         description: Unique identifier for the weather report
         example: 1
   ```

When the service tried to convert a UUID string into the integer type expected by the schema, it resulted in the type error.

## Potential Solutions

We identified two possible solutions:

1. Change the service code to convert UUIDs to integers before returning
2. Update the OpenAPI schema to use string with UUID format instead of integers

We chose the second option as it better aligned with the domain model's use of UUIDs throughout the system.

## Solution Implemented

We updated the OpenAPI schema in `docs/openapi/components/schemas/weather.yaml` to use string with UUID format:

```yaml
WeatherReport:
  type: object
  properties:
    id:
      type: string
      format: uuid
      description: Unique identifier for the weather report
      example: "123e4567-e89b-12d3-a456-426614174000"
    # ... other properties
```

Additionally, we updated example values in `docs/openapi/paths/weather.yaml` to use UUID strings instead of integers:

```yaml
responses:
  '200':
    description: The weather report for the requested city
    content:
      application/json:
        schema:
          $ref: '../components/schemas/weather.yaml#/WeatherReport'
        example:
          id: "123e4567-e89b-12d3-a456-426614174000"  # Changed from 1
          city: "London"
          # ... other properties
```

## Verification

After implementing the schema changes, GET requests to `/weather/London` began returning successful responses with UUID strings for the `id` field, confirming the fix was effective.

## Lessons Learned

1. **Schema Consistency**: Ensure consistency between API schemas and domain models from the beginning of development.

2. **UUIDs vs Integers for IDs**: Consider the trade-offs of using UUIDs (globally unique, no collision) vs integers (smaller, human-readable) for IDs early in the design process.

3. **Type System Benefits**: Strong typing in OpenAPI specs can help catch these issues earlier, especially when using tools that validate against the schema.

4. **Backward Compatibility**: When making schema changes, consider the impact on existing clients. In this case, changing from integer to string could be a breaking change for clients expecting integers. 