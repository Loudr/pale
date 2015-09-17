from pale.fields.base import BaseField

class StringField(BaseField):
    """A BaseField whose type is `string`."""
    value_type = 'string'

    def __init__(self, description, **kwargs):
        super(StringField, self).__init__(
                self.value_type,
                description,
                **kwargs)
