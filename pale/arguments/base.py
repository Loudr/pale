from pale.errors import ArgumentError

class BaseArgument(object):
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
        self.list_item_type = kwargs.pop('item_type', "*")
        super(ListArgument, self).__init__(*args, **kwargs)

    def _validate_required(self, item, name):
        super(ListArgument, self)._validate_required(item, name)
        # should we also validate that the list is not empty?

    def validate_items(self, input_list):
        """Validates that items in the list are of the type specified.

        Returns the input list if it's valid, or raises an ArgumentError if
        it's not."""
        for item in input_list:
            # we're not going to transform the list here, just make sure that
            # none of the items throw ArgumentErrors

            self.list_item_type.validate(item, self.item_name)
            # this might lead to confusing error messages.  tbh, we need to
            # figure out a better way to do validation and error handling here,
            # but i'm brute forcing this a bit so that we have something
            # workable
        return input_list


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

        validated_list = list(item)

        if self.list_item_type != "*":
            self.validate_items(validated_list)

        return validated_list
