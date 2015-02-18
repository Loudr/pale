from pale.arguments.base import BaseArgument, ListArgument
from pale.errors import ArgumentError

class StringArgument(BaseArgument):
    allowed_types = (str, unicode)

    def validate(self, item, item_name):
        if item is None:
            item = self.default

        self._validate_type(item, item_name)

        if self.required is True and \
                (item is None or str(item) == ""):
                raise ArgumentError(item_name,
                        ("This argument is required, and cannot be an empty "
                         "string."))
        if item is not None:
            item = str(item)
        return item


class StringListArgument(ListArgument):
    """StringListArgument is a special case of ListArgument that allows for
    passing in a single string as the argument, and using a separator to split
    it into a list."""
    allowed_types = (list, tuple, str, unicode)
    list_item_type = StringArgument('String list')

    def __init__(self, *args, **kwargs):
        self.separator = kwargs.pop('separator', ' ')
        super(StringListArgument, self).__init__(*args, **kwargs)

    def validate(self, item, item_name):
        if item is None:
            item = self.default

        if isinstance(item, (str, unicode)):
            item = item.split(self.separator)

        # list validation
        item = super(StringListArgument, self).validate(item, item_name)
        if item is not None:
            item = [unicode(val) for val in item]
        return item
