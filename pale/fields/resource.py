from pale.fields.base import BaseField, ListField
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


    def render(self, obj, name, context):
        if obj is None:
            output = None
        else:
            instance = getattr(obj, name, None)
            renderer = self.resource_instance._render_serializable
            output = renderer(instance, context)
        return output


class ResourceListField(ListField):
    """A Field that contains a list of Fields."""
    item_type = ResourceField

    def __init__(self,
            description,
            resource_type=Resource,
            subfields=None,
            **kwargs)
        super(ResourceListField, self).__init__(
                description,
                item_type=self.item_type,
                **kwargs)
        self.resource_type = resource_type

        if subfields is None:
            subfields = resource_type._default_fields
        self.subfields = subfields

        self.resource_instance = self.resource_type(
                'nested_resource',
                fields=self.subfields)


    def doc_dict(self):
        doc = super(ResourceListField, self).doc_dict()
        doc['resource_type'] = self.resource_type._value_type
        return doc


    def render(self, obj, name, context):
        if obj is None:
            return None

        output = []
        list_of_resources = getattr(obj, name, [])
        renderer = self.resource_instance._render_serializable
        for res in list_of_resources:
            item = renderer(res, context)
            output.append(item)
        return output
