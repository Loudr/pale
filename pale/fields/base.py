class BaseField(object):
    """The base class for all Fields and Arguments.

    Field objects are used by Resources to define the data they return.
    They include a name, a type, a short description, and a long
    description.  Of these instance variables, only `name` is functionally
    significant, as it's used as the key for the field's value in the
    outgoing JSON.  The rest of the instance variables are used to generate
    documentation.

    Argument objects inherit from Field, in that they share the same base set
    of instance variables, but are used on the input side of the API, and
    include validation functionality.
    """

    def __init__(self, value_type, description, details=None):
        self.value_type = value_type
        self.description = description
        self.details = details


    def render(self, obj, name):
        """The default field renderer.

        This basic renderer assumes that the object has an attribute with the
        same name as the field."""
        return getattr(obj, name)


    def doc_dict(self):
        """Generate the documentation for this field."""
        doc = {
            'type': self.value_type,
            'description': self.description,
            'extended_description': self.details
        }
        return doc

class ListField(BaseField):
    """A Field that contains a list of Fields."""
    value_type = 'list'

    def __init__(self, description, details=None, item_type=BaseField):
        self.description = description
        self.details = details
        self.item_type = item_type

    def doc_dict(self):
        doc = super(ListField, self).doc_dict()
        doc['item_type'] = self.item_type.value_type
        return doc
