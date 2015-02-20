import flask

from pale.adapters import flask as pale_flask_adapter

from tests.example_app import api


def create_pale_flask_app():
    """Creates a flask app, and registers a blueprint bound to pale."""
    blueprint = flask.Blueprint('api', 'test.flask_example.api_blueprint')
    pale_flask_adapter.bind_blueprint(api, blueprint)

    app = flask.Flask(__name__)
    app.register_blueprint(blueprint, url_prefix='/api')

    return app
