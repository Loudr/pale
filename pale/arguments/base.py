# -*- coding: utf-8 -*-
import json
import logging

from pale.errors import ArgumentError
from pale.fields import BaseField

class BaseArgument(BaseField):
    """The base class for Pale Arguments.

    Arguments in this context are values passed in to Pale Endpoints from the
    HTTP layer.  These Argument objects are expected to validate parameters
    received from the HTTP layer before they're propagated to the endpoint
    handler that you define in your API.

    The `validate` method in subclasses should return the value if it is
    valid (including returning None if None is a valid value), or raise an
    ArgumentError if the argument is invalid.

    The ArgumentError will generate an HTTP 422 Unprocessable Entity response,
    and propagate the message of the exception to the caller.
    """
    allowed_types = (object,)

    def __init__(self,
            short_doc,
            default=None,
            required=False,
            **kwargs):
        """Initialize an argument.

        This method is usually called from the Endpoint definition, and the
        created object is typically assigned to a key in the endpoint's 
        `arguments` dictionary.
        """
        self.description = short_doc
        self.default = default
        self.required = required
        for k, v in kwargs.iteritems():
            setattr(self, k, v)


    def validate(self, item, item_name):
        """Validate the passed in item.

        The `item_name` is passed in so that we can generate a human-readable
        and user friendly error message, but this is architecturally a bit
        cumbersome right now, so we may want to change it in the future.

        Subclasses of BaseArgument should implement their own validation
        function.
        """
        raise ArgumentError(item_name,
                ("ERROR! Your endpoint is missing a parser for your argument. "
                 "The argument validator bubbled all the way up to the base "
                 "argument, which is definitely not what you want!"))


    def _validate_type(self, item, name):
        """Validate the item against `allowed_types`."""
        if item is None:
            # don't validate None items, since they'll be caught by the portion
            # of the validator responsible for handling `required`ness
            return

        if not isinstance(item, self.allowed_types):
            item_class_name = item.__class__.__name__
            raise ArgumentError(name,
                "Expected one of %s, but got `%s`" % (
                    self.allowed_types, item_class_name))


    def _validate_required(self, item, name):
        """Validate that the item is present if it's required."""
        if self.required is True and item is None:
            raise ArgumentError(name, "This argument is required.")


    def doc_dict(self):
        """Returns the documentation dictionary for this argument."""
        doc = {
            'type': self.__class__.__name__,
            'description': self.description,
            'default': self.default,
            'required': self.required
        }
        if hasattr(self, 'details'):
            doc['detailed_description'] = self.details
        return doc


class ListArgument(BaseArgument):
    """A basic List Argument type, with flexible type support.

    This base list abstraction supports a set of allowed item types, and
    iterates through the passed in items to validate each one individually.

    If any single item is invalid, then the entire list is considered to be
    invalid, and an argument error is thrown.
    """
    allowed_types = (list, tuple)

    list_item_type = "*"

    def __init__(self, *args, **kwargs):
        self.list_item_type = kwargs.pop('item_type', self.list_item_type)
        super(ListArgument, self).__init__(*args, **kwargs)

    def _validate_required(self, item, name):
        super(ListArgument, self)._validate_required(item, name)
        # should we also validate that the list is not empty?


    def validate_items(self, input_list):
        """Validates that items in the list are of the type specified.

        Returns the input list if it's valid, or raises an ArgumentError if
        it's not."""
        output_list = []
        for item in input_list:
            valid = self.list_item_type.validate(item, self.item_name)
            output_list.append(valid)

            # this might lead to confusing error messages.  tbh, we need to
            # figure out a better way to do validation and error handling here,
            # but i'm brute forcing this a bit so that we have something
            # workable
        return output_list


    def validate(self, item, item_name):
        self.item_name = item_name
        if item is None:
            item = self.default
        self._validate_type(item, item_name)

        self._validate_required(item, item_name)

        # item might still be None if it's not required, has no default,
        # and wasn't passed in
        if item is None:
            return item

        item_list = list(item)
        validated_list = self.validate_items(item_list)
        return validated_list


class JsonDictArgument(BaseArgument):
    allowed_types = (dict, set)

    def __init__(self, *args, **kwargs):
        self.field_map = kwargs.pop('field_map', {})
        self.allow_extra_fields = kwargs.pop('allow_extra_fields', False)
        super(JsonDictArgument, self).__init__(*args, **kwargs)


    def validate(self, item, item_name):
        if isinstance(item, basestring):
            try:
                item = json.loads(item)
            except ValueError as e:
                logging.error("couldn't serialize json from item: '%s'",
                        item)
                raise ArgumentError(item_name,
                        "Invalid JSON string: '%s'" % item)

        self._validate_type(item, item_name)

        if item is None:
            return item

        item_keys = item.keys()
        field_keys = self.field_map.keys()
        extra_keys = [ k for k in item_keys if k not in field_keys ]
        missing_keys = [ k for k in field_keys if k not in item_keys ]

        if len(extra_keys) > 0 and not self.allow_extra_fields:
            raise ArgumentError(item_name,
                    "Extra keys '%s' in item are not allowed" % extra_keys)

        output_dict = dict()
        for item_key, argument in self.field_map.iteritems():
            item_value = item.get(item_key, None)

            nested_item_name = "%s.%s" % (item_name, item_key)
            validated = argument.validate(item_value, nested_item_name)
            output_dict[item_key] = validated

        for extra in extra_keys:
            val = item[extra]
            logging.debug("Adding unvalidated value '%s: %s' to json dict %s",
                    extra, val, item_name)
            output_dict[extra] = val
        return output_dict
