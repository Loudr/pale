import unittest

from webtest import TestApp

from tests.example_app.api.resources import DateTimeResource


class FlaskAdapterTests(unittest.TestCase):

    def setUp(self):
        from tests.example_app.flask_app import create_pale_flask_app
        self.flask_app = create_pale_flask_app()
        self.app = TestApp(self.flask_app)

    def test_successful_get_without_params(self):
        resp = self.app.get('/api/current_time/')
        self.assertEqual(resp.status_code, 200)

        # the 'time' value was set in the endpoint handler
        self.assertIn('time', resp.json_body)

        # the returned time value should match the resource defined
        # in tests.example_app.api.resources.py
        returned_time = resp.json_body['time']

        # the endpoint specifies `fields=DateTimeResource._all_fields()`
        # so, we should expect to find all of them
        expected_fields = DateTimeResource._all_fields()

        for f in expected_fields:
            self.assertIn(f, returned_time)
            val = returned_time.pop(f)
            # don't check the val for now
        # make sure there's extraneous left in the dict
        self.assertEqual(len(returned_time.keys()), 0)


    def test_successful_post_with_required_params(self):
        # month is required in the endpoint definition, so we must pass
        # it in here
        resp = self.app.post('/api/parse_time/', {'month': 2})

        self.assertEqual(resp.status_code, 200)
        self.assertIn('time', resp.json_body)

        returned_time = resp.json_body['time']

        # we didn't specify any other fields in the endpoint definition,
        # so this one should only get the defaults
        expected_fields = DateTimeResource._default_fields

        for f in expected_fields:
            self.assertIn(f, returned_time)
            val = returned_time.pop(f)
        self.assertEqual(len(returned_time.keys()), 0)


    def test_unsuccessful_post_missing_required_params(self):
        resp = self.app.post('/api/parse_time/', status=422)

        self.assertIn('error', resp.json_body)
