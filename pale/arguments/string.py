from pale.arguments.base import BaseArgument, ListArgument
from pale.errors import ArgumentError

class StringArgument(BaseArgument):
    allowed_types = (str, unicode)
    min_length = None
    max_length = None

    def validate(self, item, item_name):
        if item is None:
            # TODO: should we also set the default here if item is empty string?
            item = self.default

        self._validate_type(item, item_name)

        if self.required is True and \
                (item is None or unicode(item) == ""):
                raise ArgumentError(item_name,
                        ("This argument is required, and cannot be an empty "
                         "string."))
        if item is not None:
            item = unicode(item)
        return item


    def doc_dict(self):
        doc = super(StringArgument, self).doc_dict()
        doc['min_length'] = self.min_length
        doc['max_length'] = self.max_length
        return doc


class StringListArgument(ListArgument):
    """StringListArgument is a special case of ListArgument that allows for
    passing in a single string as the argument, and using a separator to split
    it into a list."""
    allowed_types = (list, tuple, str, unicode)
    list_item_type = StringArgument('String list')

    def __init__(self, *args, **kwargs):
        self.separator = kwargs.pop('separator', ' ')
        self.trim_whitespace = kwargs.pop('trim_whitespace', False)
        super(StringListArgument, self).__init__(*args, **kwargs)

    def validate(self, item_list, item_name):
        if item_list is None:
            item_list = self.default

        if isinstance(item_list, (str, unicode)):
            item_list = item_list.split(self.separator)

        if self.trim_whitespace:
            item_list = [ item.strip() for item in item_list ]

        # list validation
        item_list = super(StringListArgument, self).validate(item_list,
                                                             item_name)
        if item_list is not None:
            item_list = [unicode(val) for val in item_list]
        return item_list
