
class MetaHasFields(type):
    """Metaclass for classes that support named field definitions.

    In Pale, this is particularly Endpoint and Resource.  This metaclass is
    here to populate the developer-specified fields on the class so that
    simple API definition like the following is possible:

        class MyEndpoint(Endpoint):
            _method = 'GET'
            _uri = '/hello'

            name = StringArgument(
                description="Who should we say Hello to?",
                default="World")

            _returns = RawStringResource("A 'Hello, world' string")

            def _handle(self, context):
              return "Hello, %s" % context.args.name

    In the above case, this metaclass allows us to create a `_arguments` map
    that would store {"name": MyEndpoint.name}.
    """

    def __init__(cls, name, bases, classdict):
        super(MetaHasFields, cls).__init__(name, bases, classdict)
        cls._fix_up_fields()
