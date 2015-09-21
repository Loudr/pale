# -*- coding: utf-8 -*-
import logging

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

class MetaResource(MetaHasFields):
    """A Metaclass specific to Resources.

    This inherits MetaHasFields to resolve field names, and also adds a
    hook to add Resource classes to a resource registry so that nested
    resources can be resolved by a string class name instead of by 
    passing an instance of the actual class.

    This is here to facilitate a feature of ResourceField that would
    otherwise result in circular references:  FooResource contains a
    ResourceField with a resource_type of BarResource, and BarResource
    contains a resource_type of FooResource, which results in something
    like:

    {
        "foo": {
            "name": "A Foo",
            "id": "foo123"
            "this_foos_bar": {
                "length": 42,
                "description": "Bars can have a length",
                "other_foos": [
                    {
                        "name": "A Different Foo",
                        "id": "foo345"
                    },
                    {
                        "name": "A Third Foo, even!",
                        "id": "foo456"
                    }
                ]
            }
        }
    }
    """
    def __init__(cls, name, bases, classdict):
        super(MetaHasFields, cls).__init__(name, bases, classdict)
        cls._register_resource(name)
