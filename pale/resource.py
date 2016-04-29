import logging
import types

from pale.fields import BaseField
from pale.meta import MetaHasFields

class Resource(object):
    __metaclass__ = MetaHasFields

    _value_type = "Base Resource"

    _default_fields = None

    @classmethod
    def _all_fields(cls):
        return tuple(cls._fields.keys())

    @classmethod
    def _fix_up_fields(cls):
        """Add names to all of the Resource fields.

        This method will get called on class declaration because of
        Resource's metaclass.  The functionality is based on Google's NDB
        implementation.

        `Endpoint` does something similar for `arguments`.
        """
        cls._fields = {}
        if cls.__module__ == __name__ and cls.__name__ != 'DebugResource':
            return
        for name in set(dir(cls)):
            attr = getattr(cls, name, None)
            if isinstance(attr, BaseField):
                if name.startswith('_'):
                    raise TypeError("Resource field %s cannot begin with an "
                            "underscore.  Underscore attributes are reserved "
                            "for instance variables that aren't intended to "
                            "propagate out to the HTTP caller." % name)
                attr._fix_up(cls, name)
                cls._fields[attr.name] = attr
        if cls._default_fields is None:
            cls._default_fields = tuple(cls._fields.keys())


    def __init__(self, doc_string=None, fields=None):
        """Initialize the resource with the provided doc string and fields.

        In general, the doc string should never be none for individual
        resources, but may be none when the resource class is included as a
        part of a ResourceList or ResourceDict.
        """
        self._description = doc_string
        if fields is not None:
            self._fields_to_render = fields
        else:
            self._fields_to_render = self._default_fields


    def _render_serializable(self, obj, context):
        """Renders a JSON-serializable version of the object passed in.
        Usually this means turning a Python object into a dict, but sometimes
        it might make sense to render a list, or a string, or a tuple.

        In this base class, we provide a default implementation that assumes
        some things about your application architecture, namely, that your
        models specified in `underlying_model` have properties with the same
        name as all of the `_fields` that you've specified on a
        resource, and that all of those fields are public.

        Obviously this may not be appropriate for your app, so your
        subclass(es) of Resource should implement this method to serialize
        your things in the way that works for you.

        Do what you need to do.  The world is your oyster.
        """
        logging.info("""Careful, you're calling ._render_serializable on the
        base resource, which is probably not what you actually want to be
        doing!""")
        if obj is None:
            logging.debug(
                    "_render_serializable passed a None obj, returning None")
            return None
        output = {}
        if self._fields_to_render is None:
            return output
        for field in self._fields_to_render:
            renderer = self._fields[field].render
            output[field] = renderer(obj, field, context)
        return output



class ResourceList(Resource):
    """A wrapper around a Resource object to specify that the API will return
    a homogeneous list of multiple Resources.  This response type is used by
    `index`-style endpoints, where multiple items of the same type should be
    returned as an array.
    """
    _description = "A generic list of Resources"

    def __init__(self, doc_string, item_type, **kwargs):
        kwargs['doc_string'] = doc_string
        super(ResourceList, self).__init__(**kwargs)

        if isinstance(item_type, Resource):
            self._item_resource = item_type
        if isinstance(item_type, types.ObjectType):
            self._item_resource = item_type()
        else:
            raise ValueError("""Failed to initialize ResourceList, since it
            was passed an `item_type` other than an Instance of a Resource or
            a Resource class.""")
        self._description = "A list of %s Resources" % self._item_resource.name


    def _render_serializable(self, list_of_objs, context):
        """Iterates through the passed in `list_of_objs` and calls the
        `_render_serializable` method of each object's Resource type.

        This will probably support heterogeneous types at some point (hence
        the `item_types` initialization, as opposed to just item_type), but
        that might be better suited to something else like a ResourceDict.

        This method returns a JSON-serializable list of JSON-serializable
        dicts.
        """
        output = []
        for obj in list_of_objs:
            if obj is not None:
                item = self._item_resource._render_serializable(obj, context)
                output.append(item)
        return output


class NoContentResource(Resource):
    """An empty resource to represent endpoints that return No-Content."""
    _description = "The shell of a Resource where content used to be"

    def _render_serializable(self, obj, context):
        return None


class DebugResource(Resource):
    """A schema-less resource to help with debugging.

    This is one of the most dangerous Pale resource types, because it affords
    you the opportunity to _not define your resource_.  You should only use
    this when you're trying to define your resource fields, or on endpoints
    that you might not need to keep for the long term.
    """

    def _render_serializable(self, obj, context):
        return obj
