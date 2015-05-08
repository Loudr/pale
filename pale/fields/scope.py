from pale.fields.string import StringField

class ScopeField(StringField):
    """A field for the OAuth 2.0 Scope parameter"""
    value_type = 'oauth scope'
