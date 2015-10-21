import unittest

from webtest import TestApp

from tests.example_app.api.resources import DateTimeResource


class FlaskAdapterTests(unittest.TestCase):

    def setUp(self):
        from tests.example_app.flask_app import create_pale_flask_app
        self.flask_app = create_pale_flask_app()
        self.app = TestApp(self.flask_app)


    def assertExpectedFields(self, returned_dict, expected_fields):
        d = returned_dict.copy() # don't clobber the input

        for f in expected_fields:
            self.assertIn(f, d)
            val = d.pop(f)
            # don't check the val for now

        # make sure there's nothing extraneous left in the dict
        self.assertEqual(len(d.keys()), 0)
        return


    def test_successful_get_without_params(self):
        resp = self.app.get('/api/time/current')
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access-Control-Allow-Origin", resp.headers)
        self.assertEqual(resp.headers["Access-Control-Allow-Origin"], '*')

        # the 'time' value was set in the endpoint handler
        self.assertIn('time', resp.json_body)

        # the returned time value should match the resource defined
        # in tests.example_app.api.resources.py
        returned_time = resp.json_body['time']

        # the endpoint specifies `fields=DateTimeResource._all_fields()`
        # so, we should expect to find all of them
        expected_fields = DateTimeResource._all_fields()

        self.assertExpectedFields(returned_time, expected_fields)


    def test_successful_post_with_required_params(self):
        # month is required in the endpoint definition, so we must pass
        # it in here
        resp = self.app.post('/api/time/parse', {'month': 2})

        self.assertEqual(resp.status_code, 200)
        self.assertIn('time', resp.json_body)

        returned_time = resp.json_body['time']

        # we didn't specify any other fields in the endpoint definition,
        # so this one should only get the defaults
        expected_fields = DateTimeResource._default_fields

        self.assertExpectedFields(returned_time, expected_fields)


    def test_successful_json_post_with_required_params(self):
        # this is the same as the above post, but passes json in the
        # request body, instead of x-www-form-urlencoded
        resp = self.app.post_json('/api/time/parse', {'month': 2})

        self.assertEqual(resp.status_code, 200)
        self.assertIn('time', resp.json_body)

        returned_time = resp.json_body['time']

        # we didn't specify any other fields in the endpoint definition,
        # so this one should only get the defaults
        expected_fields = DateTimeResource._default_fields

        self.assertExpectedFields(returned_time, expected_fields)


    def test_unsuccessful_post_missing_required_params(self):
        resp = self.app.post('/api/time/parse', status=422)

        self.assertIn('error', resp.json_body)


    def test_getting_with_nested_resources(self):
        test_duration = 60 * 1000 # one minute in milliseconds
        resp = self.app.get('/api/time/range', {'duration': test_duration})

        self.assertEqual(resp.status_code, 200)
        self.assertIn('range', resp.json_body)

        returned_range = resp.json_body['range']
        self.assertEqual(returned_range['duration_microseconds'],
                test_duration * 1000)

        # start has default fields
        start = returned_range['start']
        expected_fields = DateTimeResource._default_fields
        self.assertExpectedFields(start, expected_fields)

        # end has all of them
        end = returned_range['end']
        expected_fields = DateTimeResource._all_fields()
        self.assertExpectedFields(end, expected_fields)
