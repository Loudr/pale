import unittest

from webtest import TestApp

from tests.example_app.flask_app import create_pale_flask_app


class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        self.flask_app = create_pale_flask_app()
        self.app = TestApp(self.flask_app)


    def test_successful_route_calls(self):
        """Tests against success cases.

        Call the /current_time and /parse_time endpoints with the correct
        parameters to verify that they return HTTP 200 codes, and behave
        as expected in the successful case.
        """

        # note that `create_pale_flask_app` applies a prefix of /api to
        # the uris specified in the Pale endpoints.
        resp = self.app.get('/api/current_time/')
        self.assertEqual(resp.status_code, 200)
        import pdb; pdb.set_trace()
        self.assertIn('time', resp.json_body)


        resp = self.app.post('/api/parse_time/', {'month': 2})
        self.assertEqual(resp.status_code, 200)
