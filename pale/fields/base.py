
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

    def __init__(self, name, field_type, description, details=None):
        self.name = name
        self.field_type = field_type
        self.description = description
        self.details = details


    def doc_dict(self):
        """Generate the documentation for this field."""
        doc = {
            'name': self.name,
            'type': self.field_type,
            'description': self.description,
            'extended_description': self.details
        }
        return doc
