import webapp2

from pale.adapters import webapp2 as pale_webapp2_adapter
from pale.config import authenticator, context_creator

from tests.example_app import api


@authenticator
def authenticate_pale_context(context):
    """Don't actually authenticate anything in this test."""
    return context

@context_creator
def create_pale_context(endpoint,request):
    return pale_webapp2_adapter.DefaultWebapp2Context(endpoint, request)


def create_pale_webapp2_app():
    """Creates a webapp2 WSGIApplication bound to pale."""
    app = webapp2.WSGIApplication(debug=True)
    pale_webapp2_adapter.bind_pale_to_webapp2(api,
            app,
            route_prefix='/api')
    return app
