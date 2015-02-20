import logging
import types

class Resource(object):

    available_fields = {}
    default_fields = ()

    @classmethod
    def all_fields(cls):
        return tuple(cls.available_fields.keys())

    def __init__(self, doc_string=None, fields=None):
        """Initialize the resource with the provided doc string and fields.

        In general, the doc string should never be none for individual
        resources, but may be none when the resource class is included as a
        part of a ResourceList or ResourceDict.
        """
        self.description = doc_string
        if fields is not None:
            self.fields_to_render = fields
        else:
            self.fields_to_render = self.default_fields


    def render_serializable(self, obj, context):
        """Renders a JSON-serializable version of the object passed in.
        Usually this means turning a Python object into a dict, but sometimes
        it might make sense to render a list, or a string, or a tuple.

        In this base class, we provide a default implementation that assumes
        some things about your application architecture, namely, that your
        models specified in `underlying_model` have properties with the same
        name as all of the `available_fields` that you've specified on a
        resource, and that all of those fields are public.

        Obviously this may not be appropriate for your app, so your
        subclass(es) of Resource should implement this method to serialize
        your things in the way that works for you.

        Do what you need to do.  The world is your oyster.
        """
        logging.info("""Careful, you're calling .render_serializable on the
        base resource, which is probably not what you actually want to be
        doing!""")
        output = {}
        if self.fields_to_render is None:
            return output
        for field in self.fields_to_render:
            output[field] = getattr(obj, field)
        return output



class ResourceList(Resource):
    """A wrapper around a Resource object to specify that the API will return
    a homogeneous list of multiple Resources.  This response type is used by
    `index`-style endpoints, where multiple items of the same type should be
    returned as an array.
    """
    name = "ResourceList"

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
        self.name = "ResourceList of %s" % self.item_resource.name


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
    name = "NoContent"
