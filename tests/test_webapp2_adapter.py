from webtest import TestApp

from tests.test_flask_adapter import FlaskAdapterTests


class Webapp2AdapterTests(FlaskAdapterTests):
    """Run webapp2 adapter tests.

    These tests should be the same tests as run against the Flask
    adapter, so we inherit from that class and change around what app
    the tests run against.

    Any new tests that should be run against all adapters should be added
    directly to the Flask tests.
    """

    def setUp(self):
        from tests.example_app.webapp2_app import create_pale_webapp2_app
        self.wsgi_app = create_pale_webapp2_app()
        self.app = TestApp(self.wsgi_app)
