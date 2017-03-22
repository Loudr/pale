# -*- coding: utf-8 -*-
import logging
import types

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

    value_type = 'base'

    def __init__(self,
                 value_type,
                 description,
                 details=None,
                 property_name=None,
                 value=None):
        self.value_type = value_type
        self.description = description
        self.details = details
        self.property_name = property_name
        self.value_lambda = value

        if self.value_lambda is not None:
            assert isinstance(value, types.LambdaType), \
                    "A Field's `value` parameter must be a lambda"
            assert self.property_name is None, \
                    ("Field does not support setting both `property_name` "
                     "*AND* `value`.  Please pick one or the other")


    def _fix_up(self, cls, code_name):
        """Internal helper to name the field after its variable.

        This is called by _fix_up_fields, which is called by the MetaHasFields
        metaclass when finishing the construction of a Resource subclass.

        The `code_name` passed in is the name of the python attribute that
        the Field has been assigned to in the resource.

        Note that each BaseField instance must only be assigned to at most
        one Resource class attribute.
        """
        self.name = code_name


    def render(self, obj, name, context):
        """The default field renderer.

        This basic renderer assumes that the object has an attribute with
        the same name as the field, unless a different field is specified
        as a `property_name`.

        The renderer is also passed the context so that it can be
        propagated to the `_render_serializable` method of nested
        resources (or, for example, if you decide to implement attribute
        hiding at the field level instead of at the object level).

        Callable attributes of `obj` will be called to fetch value.
        This is useful for fields computed from lambda functions
        or instance methods.
        """
        if self.value_lambda is not None:
            val = self.value_lambda(obj)
        else:
            attr_name = name
            if self.property_name is not None:
                attr_name = self.property_name
            if isinstance(obj, dict):
                val = obj.get(attr_name, None)
            else:
                val = getattr(obj, attr_name, None)

        if callable(val):
            try:
                val = val()
            except:
                logging.exception("Attempted to call `%s` on obj of type %s.",
                    attr_name, type(obj))
                raise

        return val


    def doc_dict(self):
        """Generate the documentation for this field."""
        doc = {
            'type': self.value_type,
            'description': self.description,
            'extended_description': self.details
        }
        return doc

class StaticItem(object):

    def __init__(self, obj):
        self.obj = obj

class ListField(BaseField):
    """A Field that contains a list of Fields."""

    value_type = 'list'

    def __init__(self, description, item_type=BaseField, **kwargs):
        super(ListField, self).__init__(
                self.value_type,
                description,
                **kwargs)

        # Item type initialization
        self.item_type = item_type
        kd = {'description':'nested_list'}
        if item_type is BaseField:
            kd['value_type'] = 'base_field'
        self.item_type_instance = self.item_type(
            **kd
            )


    def doc_dict(self):
        doc = super(ListField, self).doc_dict()
        doc['item_type'] = self.item_type.value_type
        return doc

    def render(self, obj, name, context):
        if obj is None:
            return []

        output = []

        # again, the base renderer basically just calls getattr.
        # We're expecting the attr to be a list, though.
        lst = super(ListField, self).render(obj, name, context)
        if lst is None:
            return []
        renderer = self.item_type_instance.render
        for res in lst:
            item = renderer(StaticItem(res), 'obj', context)
            output.append(item)
        return output

