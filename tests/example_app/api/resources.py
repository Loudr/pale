# -*- coding: utf-8 -*-
import datetime

from pale import Resource
from pale.fields import IntegerField, ResourceField, StringField

from tests.example_app.models import DateTimeModel, DateTimeRangeModel

class DateTimeResource(Resource):
    """A simple datetime resource used for testing Pale Resources."""
    _value_type = 'DateTime Resource'
    _underlying_model = DateTimeModel


    year = IntegerField("The year of the returned DateTime")
    month = IntegerField("A month, between 1 and 12")
    day = IntegerField("The date of the month")

    hours = IntegerField("The hours time, between 0 and 23")
    minutes = IntegerField("The minutes, between 0 and 59")
    seconds = IntegerField("The seconds, between 0 and 59")

    isoformat = StringField("The DateTime's ISO representation",
            property_name='iso')

    eurodate = StringField("The date in DD.MM.YYYY format",
            value=lambda item: item.timestamp.strftime("%d.%m.%Y"))

    name = StringField("Your DateTime's name",
            details="This value will be `null` on most DateTimes.  It's "
            "only set when the DateTime is created with `/parse_time/` "
            "and a `name` is passed in.")


    _default_fields = ('year',
                       'month',
                       'day',
                       'isoformat')


    def _render_serializable(self, instance, context):
        """Render a datetime for the context provided"""
        if not isinstance(instance, DateTimeModel):
            """This check is here for illustration purposes, but isn't
            strictly required, as long as you make sure you send the correct
            objects to their correct serializers."""
            raise ValueError(("You broke the test app by trying to pass "
                "something other than a `DateTimeModel` to the "
                "DateTimeResource serializer."))

        output = super(DateTimeResource, self)._render_serializable(
                instance, context)

        # add fields based on the instance state
        if instance.include_time:
            output['hours'] = instance.hours
            output['minutes'] = instance.minutes
            output['seconds'] = instance.seconds

        if instance.name is not None:
            output['name'] = instance.name

        # Typically, the context is also used to selectively render (or hide)
        # specific fields based on the current user, and whether or not they own
        # the object that they're trying to obtain.

        # But we're not doing that in this example.

        return output


class DateTimeRangeResource(Resource):
    """A time range that returns some nested resources"""

    _value_type = "DateTime Range Resource"
    _underlying_model = DateTimeRangeModel


    duration_microseconds = IntegerField(
            "The range's duration in microseconds.")

    start = ResourceField("The starting datetime of the range.",
            resource_type=DateTimeResource)

    end = ResourceField(
            "The ending datetime of the range.",
            resource_type=DateTimeResource,
            subfields=DateTimeResource._all_fields())

    # default to all fields, and use the default _render_serializable
