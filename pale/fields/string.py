from pale.fields.base import BaseField

class StringField(BaseField):
    """A BaseField whose type is `string`."""
    value_type = 'string'

    def __init__(self, description, details=None):
        self.description = description
        self.details = details
