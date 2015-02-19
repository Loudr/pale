import datetime

from pale import Resource

from tests.example_app.models import DateTimeModel

class DateTimeResource(Resource):
    """A simple datetime resource used for testing Pale Resources."""
    model = DateTimeModel
    name = "DateTime"

    def render_serializable(self, instance, context):
        """Renders the `instance` of datetime for the context provided.
        """

        if not isinstance(instance, DateTimeModel):
            """This check is here for illustration purposes, but isn't
            strictly required, as long as you make sure you send the correct
            objects to their correct serializers."""
            raise ValueError(("You broke the test app by trying to render "
                "something other than a `datetime.datetime` to the "
                "DateTimeResource serializer."))

        # call the default Pale renderer based on the default_fields of the
        # model set on line 9
        output = super(DateTimeResource, self).render_serializable(
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
