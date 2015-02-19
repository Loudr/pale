from pale.errors import ArgumentError

class BaseArgument(object):

    def __init__(self,
            short_doc,
            **kwargs):
        self.description = short_doc
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def validate(self, item, item_name):
        raise ArgumentError(item_name,
                ("ERROR! Your endpoint is missing a parser for your argument. "
                 "The argument validator bubbled all the way up to the base "
                 "argument, which is definitely not what you want!"))

    def _validate_type(self, item, name):
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
        if self.required is True and item is None:
            raise ArgumentError(name, "This argument is required.")



class ListArgument(BaseArgument):
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
