import datetime

from multiprocessing import Manager

from pale import Endpoint, PatchEndpoint, PutResourceEndpoint
from pale.arguments import BooleanArgument, IntegerArgument, StringArgument
from pale.resource import DebugResource, NoContentResource
from pale.errors.api_error import APIError
from tests.example_app.models import DateTimeModel, DateTimeRangeModel
from tests.example_app.api.resources import (DateTimeResource,
        DateTimeRangeResource)


def add_after_response_test(context, response):
    """Adds a test definition to the response header."""
    response.headers['After-Response'] = "OK"

class CurrentTimeEndpoint(Endpoint):
    """An API endpoint to get the current time."""
    _http_method = "GET"
    _uri = "/time/current"
    _route_name = "current_time"
    _allow_cors = True

    _returns = DateTimeResource(
        "The DateTimeResource representation of the current time on the "
        "server.",
        fields=DateTimeResource._all_fields())

    _after_response_handlers = (add_after_response_test, )

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

    _default_cache = 'max-age=3'


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

"""
Resource endpoints.
We create a multiprocessing memory manager and shared
dict to enable multithreaded support.
This 'resource' data is used to test patching.
"""

BASE_RESOURCE = {
    'key': 'value'
}
MANAGER = Manager()
RESOURCE = MANAGER.dict(BASE_RESOURCE)

class GetResourceEndpoint(Endpoint):
    """Returns the 'resource' as it exists in memory.
    """

    _uri = "/resource"
    _http_method = 'GET'
    _route_name = "resource_get"

    _returns = DebugResource("app resource.")

    def _handle(self, context):
        return dict(RESOURCE)


class RouteArgEndpoint(Endpoint):
    """Returns the arguments as provided from URI.
    """

    _uri = "/arg_test/<arg_a>/<arg_b>"
    _http_method = 'GET'
    _route_name = "arg_test"

    _returns = DebugResource("app resource.")

    def _handle(self, context):
        arg_a = context.route_kwargs.get('arg_a', 'no')
        arg_b = context.route_kwargs.get('arg_b', 'no')
        return {"arg_a": arg_a, "arg_b": arg_b}


class ResetResourceEndpoint(Endpoint):
    """Returns the 'resource' as it exists in memory.
    """

    _uri = "/resource/reset"
    _http_method = 'POST'
    _route_name = "resource_reset"

    _returns = DebugResource("app resource.")

    def _handle(self, context):
        RESOURCE.clear()
        RESOURCE.update(BASE_RESOURCE)
        return dict(RESOURCE)

class ResourcePatchEndpoint(PatchEndpoint):
    """Patches a resource which is local to each instance of the app.
    """

    _uri = "/resource"
    _route_name = "resource_patch"

    _resource = DebugResource("resource patch.")
    _returns = DebugResource("app resource.")

    def _handle_patch(self, context, patch):
        data = dict(RESOURCE)
        patch.apply_to_dict(data)
        RESOURCE.update(data)
        return dict(RESOURCE)


class ResourceCreateEndpoint(PutResourceEndpoint):
    """Patches a resource which is local to each instance of the app.
    """

    _uri = "/resource"
    _route_name = "resource_put"

    _resource = DebugResource("resource patch.")
    _returns = DebugResource("app resource.")

    def _handle_put(self, context, patch):
        data = {}
        patch.apply_to_dict(data)
        RESOURCE.clear()
        RESOURCE.update(data)
        return dict(RESOURCE)


class BlankEndpoint(Endpoint):
    """ This carries out some action, then returns nothing on success.
    """
    _http_method = "POST"
    _uri = "/blank"
    _route_name = "resource_blank"
    _allow_cors = True

    _returns = NoContentResource()

    def _handle(self, context):
        return None