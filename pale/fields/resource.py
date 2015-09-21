# -*- coding: utf-8 -*-
import logging

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
        self.subfields = subfields
        self.resource_type = resource_type
        self._resource_type_resolved = False

        if isinstance(resource_type, basestring):
            self._defer_resource_type_resolution = True
            self._resource_type_resolved = False
            self.resource_instance = None
        else:
            self._defer_resource_type_resolution = False
            self._resolve_resource_type()

    def _resolve_resource_type(self):
        if not self._resource_type_resolved:
            if isinstance(self.resource_type, basestring):
                resource_type_class = Resource._registered_resources.get(
                        self.resource_type)
                if resource_type_class is None:
                    logging.warn("Could not find registered resource %s",
                            self.resource_type)
                    raise Exception("Invalid resource name %s",
                            self.resource_type)
                self.resource_type = resource_type_class
            if self.subfields is None:
                self.subfields = self.resource_type._default_fields
            self.resource_instance = self.resource_type(
                    'nested_resource',
                    fields=self.subfields)
            self._resource_type_resolved = True


    def doc_dict(self):
        doc = super(ResourceField, self).doc_dict()
        self._resolve_resource_type()
        doc['resource_type'] = self.resource_type._value_type
        doc['default_fields'] = self.subfields


    def render(self, obj, name, context):
        if obj is None:
            return None
        # the base renderer basically just calls getattr, so it will
        # return the resource here
        resource = super(ResourceField, self).render(obj, name, context)
        self._resolve_resource_type()
        renderer = self.resource_instance._render_serializable
        output = renderer(resource, context)
        return output


class ResourceListField(ListField):
    """A Field that contains a list of Fields."""
    item_type = ResourceField

    def __init__(self,
            description,
            resource_type=Resource,
            subfields=None,
            **kwargs):
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
        # again, the base renderer basically just calls getattr.
        # We're expecting the attr to be a list, though.
        resources = super(ResourceListField, self).render(obj, name, context)
        renderer = self.resource_instance._render_serializable
        for res in resources:
            item = renderer(res, context)
            output.append(item)
        return output
