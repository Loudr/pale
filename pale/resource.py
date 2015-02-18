import logging
import types

class Resource(object):

    def __init__(self, doc_string=None, fields=None):
        """Initialize the resource with the provided doc string and fields.

        In general, the doc string should never be none for individual
        resources, but may be none when the resource class is included as a
        part of a ResourceList or ResourceDict.
        """
        self.description = doc_string
        if fields is None:
            fields = self.default_fields()
        self.fields = fields


    def default_fields(self):
        """The base Resource attempts to look for a `model` attribute on the
        instance, and if it's present, attempts to find the `default_fields`
        attribute on the model.  If either of those is missing, it will return
        an empty fieldset.

        If you need to do anything more fancy for your Resource, you should
        subclass this method and do what you need to do.
        """
        if hasattr(self, 'model') and hasattr(self.model, 'default_fields'):
            return self.model.default_fields

        logging.warn("""The base Resource class couldn't find `self.model` or
        `self.model.default_fields`, so it's returning an empty field set.
        This is probably not what you want!""")
        return ()


    def render_serializable(self, obj, context):
        """Renders a JSON-serializable version of the object passed in.
        Usually this means turning a Python object into a dict, but sometimes
        it might make sense to render a list, or a string, or a tuple.

        Your subclass(es) of Resource should implement this method to serialize
        your things.

        Do what you need to do.  The world is your oyster.
        """
        logging.error("""Careful, you're calling .render_serializable on the
        base resource, which is probably not what you actually want to be
        doing!""")


class ResourceList(Resource):
    """A wrapper around a Resource object to specify that the API will return
    a homogeneous list of multiple Resources.  This response type is used by
    `index`-style endpoints, where multiple items of the same type should be
    returned as an array.
    """

    def __init__(self, doc_string, item_type):
        super(ResourceList, self).__init__(doc_string)

        if isinstance(item_type, Resource):
            self.item_resource = item_type
        if isinstance(item_type, types.ObjectType):
            self.item_resource = item_type()
        else:
            raise ValueError("""Failed to initialize ResourceList, since it was
            passed an `item_type` other than an Instance of a Resource or a
            Resource class.""")


    def render_serializable(self, list_of_objs, context):
        """Iterates through the passed in `list_of_objs` and calls the
        `render_serializable` method of each object's Resource type.

        This will probably support heterogeneous types at some point (hence the
        `item_types` initialization, as opposed to just item_type), but that
        might be better suited to something else like a ResourceDict.

        This method returns a JSON-serializable list of JSON-serializable dicts.
        """
        output = []
        for obj in list_of_objs:
            item = self.item_resource.render_serializable(obj, context)
            output.append(item)
        return output


class NoContentResource(Resource):
    """An empty resource to represent endpoints that return No-Content."""
    pass
