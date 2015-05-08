from pale.fields.string import StringField

class URLField(StringField):
    """A String field that has a URL in it."""
    value_type = 'url'
