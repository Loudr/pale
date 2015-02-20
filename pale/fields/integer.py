from pale.fields.base import BaseField

class IntegerField(BaseField):
    """A BaseField whose type is `integer`."""
    value_type = 'integer'

    def __init__(self, description, details=None):
        self.description = description
        self.details = details
