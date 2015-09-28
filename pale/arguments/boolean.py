# -*- coding: utf-8 -*-
from pale.errors import ArgumentError
from .base import BaseArgument

class BooleanArgument(BaseArgument):
    allowed_types = (bool, )

    def validate(self, item, item_name):
        if item is None:
            item = self.default

        if isinstance(item, (str, unicode)):
            # coerce string types to bool, since we might get a string type
            # from the HTTP library
            val = item.lower()
            if val == 'true':
                item = True
            elif val == 'false':
                item = False
            else:
                raise ArgumentError(item_name,
                        "Invalid string value '%s'. "
                        "Boolean arguments must be either 'true' or 'false'.")

        self._validate_type(item, item_name)

        if self.required is True and item is None:
            raise ArgumentError(item_name, "This argument is required.")

        return item
