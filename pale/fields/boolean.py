from pale.fields.base import BaseField

class BooleanField(BaseField):
    """A BaseField whose type is `boolean`."""
    value_type = 'boolean'

    def __init__(self, description, details=None):
        super(BooleanField, self).__init__(self.value_type,
                description,
                details)
