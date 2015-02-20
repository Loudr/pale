from pale.fields.base import BaseField

class StringField(BaseField):
    """A BaseField whose type is `string`."""
    field_type = 'string'

    def __init__(self, name, description, details=None):
        self.name = name
        self.description = description
        self.details = details
