import logging
import flask

from pale.adapters import flask as pale_flask_adapter
from pale.config import authenticator, context_creator

from tests.example_app import api

@authenticator
def authenticate_pale_context(context):
    """Don't actually authenticate anything in this test."""
    logging.debug("pale.example_app: authenticate_pale_context")
    return context

@context_creator
def create_pale_context(endpoint,request):
    logging.debug("pale.example_app: create_pale_context")
    return pale_flask_adapter.DefaultFlaskContext(endpoint, request)


def create_pale_flask_app():
    """Creates a flask app, and registers a blueprint bound to pale."""
    blueprint = flask.Blueprint('api', 'tests.example_app')
    pale_flask_adapter.bind_blueprint(api, blueprint)

    app = flask.Flask(__name__)
    app.register_blueprint(blueprint, url_prefix='/api')

    return app
