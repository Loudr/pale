from pale.fields.base import BaseField, ListField
from pale.resource import Resource


class ResourceField(BaseField):
    """A field that contains a nested resource"""

    value_type = 'resource'


    def __init__(self,
            description,
            resource_type=Resource,
            subfields=None,
            **kwargs):
        super(ResourceField, self).__init__(
                self.value_type,
                description,
                **kwargs)
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
        doc['default_fields'] = list(self.subfields)
        return doc


    def render(self, obj, name, context):
        if obj is None:
            return None
        # the base renderer basically just calls getattr, so it will
        # return the resource here
        resource = super(ResourceField, self).render(obj, name, context)
        renderer = self.resource_instance._render_serializable
        output = renderer(resource, context)
        return output


class ResourceListField(BaseField):
    """A Field that contains a list of Fields."""
    item_type = ResourceField
    value_type = 'resource_list'

    def __init__(self,
            description,
            resource_type=Resource,
            subfields=None,
            **kwargs):
        super(ResourceListField, self).__init__(
                self.value_type,
                description=description,
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
        # again, the base renderer basically just calls getattr.
        # We're expecting the attr to be a list, though.
        resources = super(ResourceListField, self).render(obj, name, context)
        renderer = self.resource_instance._render_serializable
        for res in resources:
            item = renderer(res, context)
            output.append(item)
        return output

