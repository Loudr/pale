from pale.fields.base import BaseField
from pale.resource import Resource


class ResourceField(BaseField):
    """A field that contains a nested resource"""

    value_type = 'resource'


    def __init__(self,
            description,
            details=None,
            resource_type=Resource,
            subfields=None):
        self.description = description
        self.details = details
        self.resource_type = resource_type

        if subfields is None:
            subfields = resource_type._default_fields
        self.subfields = subfields

        self.resource_instance = self.resource_type(
                'nested_resource',
                fields=self.subfields)

    def doc_dict(self):
        doc = super(ResourceField, self).doc_dict()
        doc['resource_type'] = self.resource_type._value_type
        doc['default_fields'] = self.subfields

    def render(self, obj, name):
        instance = getattr(obj, name)
        output = self.resource_instance.render(instance)
        return output
