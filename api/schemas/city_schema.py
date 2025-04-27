from marshmallow import Schema, fields, validate, post_load
from api.models.domain import City


class CitySchema(Schema):
    """Schema for serializing and deserializing City objects."""
    
    id = fields.UUID(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1))
    country = fields.String(required=True, validate=validate.Length(min=2))
    location_id = fields.UUID(required=True)
    
    @post_load
    def make_city(self, data, **kwargs):
        """Convert the validated data into a City object."""
        return City(**data) 