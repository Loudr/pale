from __future__ import absolute_import
import string
import urlparse

from pale.arguments.string import StringArgument
from pale.errors import ArgumentError


class URLArgument(StringArgument):

    def __init__(self, *args, **kwargs):
        self.path_only = kwargs.pop('path_only', False)
        super(URLArgument, self).__init__(*args, **kwargs)

    def validate_url(self, original_string):
        """Returns the original string if it was valid, raises an argument
        error if it's not.
        """

        # nipped from stack overflow: http://stackoverflow.com/questions/827557/how-do-you-validate-a-url-with-a-regular-expression-in-python
        # I preferred this to the thorough regex approach for simplicity and
        # readability
        pieces = urlparse.urlparse(original_string)
        try:
            if self.path_only:
                assert not any([pieces.scheme, pieces.netloc])
                assert pieces.path
            else:
                assert all([pieces.scheme, pieces.netloc])
                valid_chars = set(string.letters + string.digits + ":-_.")
                assert set(pieces.netloc) <= valid_chars
                assert pieces.scheme in ['http', 'https']

        except AssertionError as e:
            raise ArgumentError(self.item_name,
                    "The input you've provided is not a valid URL.")
        return pieces

    def validate(self, item, item_name):
        self.item_name = item_name
        item = super(URLArgument, self).validate(item, item_name)

        if item is not None:
            item = self.validate_url(item)
        return item
