from pale.fields.string import StringField

class TimestampField(StringField):
    """A field for timestamp strings."""
    value_type = 'timestamp'
