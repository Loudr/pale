# -*- coding: utf-8 -*-
import datetime
import unittest

from webtest import TestApp, AppError

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
        now = datetime.datetime.now()
        resp = self.app.get('/api/time/current')
        self.assertEqual(resp.status_code, 200)
        # Test _after_response_handlers
        self.assertIn("After-Response", resp.headers)
        self.assertEqual(resp.headers["After-Response"], 'OK')
        # Test CORS
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
        self.assertEqual(returned_time['eurodate'],
                now.strftime("%d.%m.%Y"))


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

        self.assertIn('Cache-Control', resp.headers)
        self.assertEqual('max-age=3', resp.headers['Cache-Control'])


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

    def test_resource(self):

        # Start by resetting the resource.
        # (multiple test runs from the same process will fail otherwise)
        resp = self.app.post('/api/resource/reset')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {'key': 'value'})

        # Test retrieving the resource.
        resp = self.app.get('/api/resource')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {'key': 'value'})

        # Test patching the resource.
        # Without the correct Content-Type, we expect a 415 error.
        self.assertRaises(AppError, self.app.patch_json,
            '/api/resource', {'key': 'value2'})

        resp = self.app.patch_json('/api/resource', {'key': 'value2'},
            headers={'Content-Type': 'application/merge-patch+json'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {'key': 'value2'})

        # Test get to ensure the resource persists.
        resp = self.app.get('/api/resource')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {'key': 'value2'})
