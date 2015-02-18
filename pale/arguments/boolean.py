from .base import BaseArgument

class BooleanArgument(BaseArgument):
    allowed_types = (bool, )

    def validate(self, item, item_name):
        if item is None:
            item = self.default

        if isinstance(item, (str, unicode)):
            # coerce string types to bool, since we might get a string type'
            # from the HTTP library
            val = item
            if val == 'true' or val == 'True':
                item = True
            elif val == 'false' or val == 'False':
                item = False

        self._validate_type(item, item_name)

        if self.required is True and item is None:
            raise ArgumentError("This argument is required.")

        return item
