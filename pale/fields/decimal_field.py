from pale.fields.base import BaseField
from decimal import Decimal

class DecimalField(BaseField):
    """A BaseField whose type is to be handled by `decimal.Decimal`.

    kwargs:
        quantize:
            `str`. Used with Decimal.quantize, which rounds the
            value to a given digit precision.

        prefix:
            `str`. String to prepend to the output. Useful for prefixing currencies.

    Usage:
        dollar_amount = DecimalField("Dollar amount rounded to nearest penny",
            quantize='.01',
            prefix='$')

    """

    value_type = 'decimal'

    def __init__(self, description, **kwargs):
        quantize = kwargs.pop('quantize', None)
        if quantize:
            self.quantize = Decimal(quantize)

        self.prefix = kwargs.pop('prefix', None) or ''

        super(DecimalField, self).__init__(
                self.value_type,
                description,
                **kwargs)

    def render(self, obj, name, context):
        if obj is None:
            return None
        value = super(DecimalField, self).render(obj, name, context)
        if value is None:
            return None
        value = Decimal(value)
        if self.quantize:
            value = value.quantize(self.quantize)

        return self.prefix+str(value)

