from pale.fields.base import BaseField

class IntegerField(BaseField):
    """A BaseField whose type is `integer`."""
    value_type = 'integer'

    def __init__(self, description, **kwargs):
        super(IntegerField, self).__init__(
                self.value_type,
                description,
                **kwargs)
