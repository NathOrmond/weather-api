from marshmallow import Schema, fields, validate, post_load
from api.models.domain import Location


class LocationSchema(Schema):
    """Schema for serializing and deserializing Location objects."""
    
    id = fields.UUID(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1))
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))
    elevation = fields.Float(required=True)
    timezone = fields.String(required=True)
    
    @post_load
    def make_location(self, data, **kwargs):
        """Convert the validated data into a Location object."""
        return Location(**data) 