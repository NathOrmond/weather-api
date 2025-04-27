from marshmallow import Schema, fields, validate, post_dump, pre_dump


class WeatherReportCreateSchema(Schema):
    """Schema for creating a new weather report."""
    
    city = fields.String(required=True)
    temperature = fields.Float(required=True)
    condition = fields.String(required=True, validate=validate.OneOf(
        ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy", "Foggy"]
    ))
    timestamp = fields.DateTime(required=False)
    humidity = fields.Float(required=False, validate=validate.Range(min=0, max=100))


class WeatherReportSchema(Schema):
    """Schema for serializing weather reports."""
    
    id = fields.UUID()
    city = fields.String(required=True)
    temperature = fields.Float(required=True)
    condition = fields.String(required=True)
    timestamp = fields.String(required=True)


class CityWeatherSummarySchema(Schema):
    """Schema for city weather summary item."""
    
    city = fields.String(required=True)
    temperature = fields.Float(required=True)
    condition = fields.String(required=True)
    timestamp = fields.String(required=True)


class WeatherSummarySchema(Schema):
    """Schema for multiple city weather summaries."""
    
    cities = fields.List(fields.Nested(CityWeatherSummarySchema), required=True)
    
    @post_dump
    def ensure_structure(self, data, **kwargs):
        """Ensure data has the expected structure when returning from the service."""
        # If data is None, return a minimal valid response
        if data is None:
            return {"cities": []}
            
        # The data should already have a 'cities' key from the service,
        # but if for some reason it doesn't, transform it
        if not isinstance(data.get('cities'), list):
            return {"cities": []}
            
        return data 