from pale.errors.validation import ArgumentError

from .base import BaseArgument

class IntegerArgument(BaseArgument):
    value_type = 'integer'
    allowed_types = (int, long)
    min_value = None
    max_value = None

    def validate(self, item, item_name):
        if item is None:
            item = self.default

        if item is None: # i.e. the default was also None
            if self.required:
                raise ArgumentError(item_name,
                        "This argument is required.")
            else:
                return item

        # it's an integer, so just try to shove it into that.
        try:
            item = int(item)
        except ValueError as e:
            # if it fails, then the argument is wrong
            raise ArgumentError(item_name,
                    "%s is not a valid integer" % item)

        # range checking
        if self.min_value is not None and\
                self.max_value is not None and\
                not (self.min_value <= item <= self.max_value):
            raise ArgumentError(item_name,
                    "You must provide a value between %d and %d" % (
                        self.min_value, self.max_value))

        if self.min_value is not None and item < self.min_value:
            raise ArgumentError(item_name,
                    "You must provide a value greater than or equal to %d" % (
                        self.min_value))

        if self.max_value is not None and item > self.max_value:
            raise ArgumentError(item_name,
                    "You must provide a value less than or equal to %d" % (
                        self.max_value))

        return item


    def doc_dict(self):
        doc = super(IntegerArgument, self).doc_dict()
        doc['min_value'] = self.min_value
        doc['max_value'] = self.max_value
        return doc


class FloatArgument(BaseArgument):
    value_type = 'float'
    allowed_types = (float, )
    min_value = None
    max_value = None

    def validate(self, item, item_name):
        if item is None:
            item = self.default

        if item is None: # i.e. the default was also None
            if self.required:
                raise ArgumentError(item_name,
                        "This argument is required.")
            else:
                return item

        # it's an integer, so just try to shove it into that.
        try:
            item = float(item)
        except ValueError as e:
            # if it fails, then the argument is wrong
            raise ArgumentError(item_name,
                    "%s is not a valid integer" % item)

        # range checking
        if self.min_value is not None and\
                self.max_value is not None and\
                not (self.min_value <= item <= self.max_value):
            raise ArgumentError(item_name,
                    "You must provide a value between %d and %d" % (
                        self.min_value, self.max_value))

        if self.min_value is not None and item < self.min_value:
            raise ArgumentError(item_name,
                    "You must provide a value greater than or equal to %d" % (
                        self.min_value))

        if self.max_value is not None and item > self.max_value:
            raise ArgumentError(item_name,
                    "You must provide a value less than or equal to %d" % (
                        self.max_value))

        return item


    def doc_dict(self):
        doc = super(FloatArgument, self).doc_dict()
        doc['min_value'] = self.min_value
        doc['max_value'] = self.max_value
        return doc
