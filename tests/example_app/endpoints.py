import datetime

from pale import Endpoint
from tests.example_app.models import DateTimeModel
from tests.example_app.resources import DateTimeResource

class CurrentTimeEndpoint(Endpoint):
    """An API endpoint to get the current time.
    """
    name = "current_time"
    method = "GET"
    uri = "/current_time/"

    returns = DateTimeResource(
        "The DateTimeResource representation of the current time on the \
        server.",
        fields=DateTimeModel.all_fields)

    def handle(self, context):
        now = DateTimeModel(datetime.datetime.utcnow())
        return {'time': now}


class ParseTimeEndpoint(Endpoint):
    """Parses some passed in parameters to generate a corresponding
    DateTimeResource.
    """
    name = "parse_time"
    method = "POST"
    uri = "/parse_time/"

    arguments = {
        'year': IntegerArgument("The year for your returned datetime",
              long_doc="""The returned time will be from the year that you
              specify""",
              default=2015),

        'month': IntegerArgument("The month for your returned datetime",
              long_doc="""The returned time will be from the month that you
              specify.""",
              required=True,
              min_value=1,
              max_value=12),

        'day': IntegerArgument("The day for your returned datetime",
              long_doc="""Any day of your choosing, within the calendar month.
              If this parameter is omitted, the returned datetime will default
              to today's date.  If today's date is not valid for the month
              specified, (i.e. today is the 31st and the specified month is
              February), then mysterious things might happen!"""),

        'name': StringArgument("The name for your datetime",
              long_doc="""You can give your time a name, which will be
              returned back to you in the response, as the field `name`.
              If you omit this input parameter, your response won't include
              a `name`.""",
              min_length=3,
              max_length=20),

          'include_time': BooleanArgument("Include the time in the output?",
              long_doc="""If present, the response will include JSON fields for the
      current time, including `hours`, `minutes`, and `second`""",
      default=False)
          }

    returns = DateTimeResource(
            """The DateTimeResource corresponding to the timing information
            sent in by the requester.""")


    def handle(self, context):
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
