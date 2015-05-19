import datetime

from pale import Endpoint
from pale.arguments import BooleanArgument, IntegerArgument, StringArgument
from tests.example_app.models import DateTimeModel, DateTimeRangeModel
from tests.example_app.api.resources import (DateTimeResource,
        DateTimeRangeResource)


class CurrentTimeEndpoint(Endpoint):
    """An API endpoint to get the current time."""
    _http_method = "GET"
    _uri = "/time/current"
    _route_name = "current_time"

    _returns = DateTimeResource(
        "The DateTimeResource representation of the current time on the "
        "server.",
        fields=DateTimeResource._all_fields())

    def _handle(self, context):
        now = DateTimeModel(datetime.datetime.utcnow())
        return {'time': now}


class ParseTimeEndpoint(Endpoint):
    """Parses some passed in parameters to generate a corresponding
    DateTimeResource.
    """
    _http_method = "POST"
    _uri = "/time/parse"
    _route_name = "parse_time"


    _returns = DateTimeResource(
            "The DateTimeResource corresponding to the timing "
            "information sent in by the requester.")


    year = IntegerArgument("Set the year of the returned datetime",
            default=2015)

    month = IntegerArgument("Set the month of the returned datetime",
            required=True,
            min_value=1,
            max_value=12)

    day = IntegerArgument("Set the day of the returned datetime")

    name = StringArgument("The name for your datetime",
            details="You can give your time a name, which will be "
            "returned back to you in the response, as the field `name`. "
            "If you omit this input parameter, your response won't "
            "include a `name`.",
            min_length=3,
            max_length=20)

    include_time = BooleanArgument("Include the time in the output?",
            details="If present, the response will include JSON fields "
            "for the current time, including `hours`, `minutes`, and "
            "`seconds`.",
            default=False)


    def _handle(self, context):
        now = DateTimeModel(datetime.datetime.utcnow())

        now.update_date(
                # year has a default, so it will always be present
                context.args['year'],

                # month is required, so it will always be present
                context.args['month'],
                context.args.get('day', None))
        now.set_include_time(context.args['include_time'])
        now.name = context.args.get('name', None)

        return {'time': now}


class TimeRangeEndpoint(Endpoint):
    """Returns start and end times based on the passed in duration.

    The start time is implied to be "now", and the end time is calculated
    by adding the duration to that start time.

    This is obviously fairly contrived, but this endpoint is here to
    illustrate and test nested resources.
    """

    _http_method = "GET"
    _uri = "/time/range"
    _route_name = "time_range_now_plus_duration"


    _returns = DateTimeRangeResource(
            "Information about the range specified, as well as the "
            "range's start and end datetimes.")


    duration = IntegerArgument(
            "The duration in milliseconds to be used.",
            required=True)


    def _handle(self, context):
        millis = context.args['duration']
        time_range = DateTimeRangeModel(millis*1000) # microseconds
        return {'range': time_range}
