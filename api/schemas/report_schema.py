from marshmallow import Schema, fields, validate, post_load
from api.models.domain import Report, ReportCondition, TemperatureUnit


class ReportSchema(Schema):
    """Schema for serializing and deserializing Report objects."""
    
    id = fields.UUID(dump_only=True)
    location_id = fields.UUID(required=True)
    timestamp = fields.DateTime(required=True)
    source = fields.String(required=True)
    temperature_current = fields.Float(required=True, data_key="temperature")
    temperature_unit = fields.Enum(TemperatureUnit, by_value=True, required=True)
    humidity = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    
    @post_load
    def make_report(self, data, **kwargs):
        """Convert the validated data into a Report object."""
        return Report(**data)


class ReportConditionSchema(Schema):
    """Schema for serializing and deserializing ReportCondition objects."""
    
    id = fields.UUID(dump_only=True)
    report_id = fields.UUID(required=True)
    condition_id = fields.UUID(required=True)
    
    @post_load
    def make_report_condition(self, data, **kwargs):
        """Convert the validated data into a ReportCondition object."""
        return ReportCondition(**data) 