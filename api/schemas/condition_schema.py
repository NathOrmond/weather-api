from marshmallow import Schema, fields, validate, post_load
from api.models.domain import Condition, ConditionType, IntensityLevel


class ConditionSchema(Schema):
    """Schema for serializing and deserializing Condition objects."""
    
    id = fields.UUID(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1))
    type = fields.Enum(ConditionType, by_value=True, required=True)
    intensity = fields.Enum(IntensityLevel, by_value=True, required=True)
    
    @post_load
    def make_condition(self, data, **kwargs):
        """Convert the validated data into a Condition object."""
        return Condition(**data) 