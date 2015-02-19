import unittest

from pale.doc import generate_doc_dict, generate_json_docs

class PaleDocTests(unittest.TestCase):
    def setUp(self):
        super(PaleDocTests, self).setUp()


    def test_generate_json(self):
        """The expectations in this test are based on the example project
        located in `tests/example_app`.
        """
        from tests import example_app
        doc_dict = generate_doc_dict(example_app)

        self.assertTrue('endpoints' in doc_dict)
        self.assertTrue(isinstance(doc_dict['endpoints'], (dict)))

        endpoints = doc_dict['endpoints']
        self.validate_example_app_endpoint_doc(endpoints)

        resources = doc_dict['resources']
        self.validate_example_app_resource_doc(resources)

    def validate_example_app_endpoint_doc(self, endpoint_dict):
        # we defined two endpoints in the example app
        self.assertEqual(len(endpoint_dict), 2)

        # the current time endpoint
        current_time_doc = endpoint_dict['current_time']

        self.assertEqual(current_time_doc['uri'], '/current_time/')
        self.assertEqual(current_time_doc['method'], 'GET')
        self.assertEqual(current_time_doc['arguments'], None)

        return_doc = current_time_doc['returns']
        self.assertEqual(return_doc['description'],
                "The DateTimeResource representation of the current time on the server.")
        self.assertEqual(return_doc['resource_name'], 'DateTime')
        self.assertEqual(return_doc['resource_type'], 'DateTimeResource')


        parse_time_doc = endpoint_dict['parse_time']

        self.assertEqual(parse_time_doc['uri'], '/parse_time/')
        self.assertEqual(parse_time_doc['method'], 'POST')

        args = parse_time_doc['args']
        self.assertEqual(len(args), 5)

        self.assertTrue('year' in args)
        self.assertTrue('month' in args)
        self.assertTrue('day' in args)
        self.assertTrue('name' in args)
        self.assertTrue('include_time' in args)

        # the year argument
        year_arg = args['year']
        self.assertEqual(year_arg['description'],
                "Set the year of the returned datetime")
        self.assertFalse('detailed_description' in year_arg)
        self.assertEqual(year_arg['type'], 'IntegerArgument')
        self.assertEqual(year_arg['default'], 2015)
        self.assertEqual(year_arg['required'], False)

        # month, which has min and max values
        month_arg = args['month']
        self.assertEqual(month_arg['description'],
                "Set the month of the returned datetime")
        self.assertFalse('detailed_description' in month_arg)
        self.assertEqual(month_arg['type'], 'IntegerArgument')
        self.assertEqual(month_arg['default'], None)
        self.assertEqual(month_arg['min_value'], 1)
        self.assertEqual(month_arg['min_value'], 12)
        self.assertEqual(month_arg['required'], False)

        # day, which is barebones
        day_arg = args['day']
        self.assertEqual(day_arg['description'],
                "Set the day of the returned datetime")
        self.assertFalse('detailed_description' in day_arg)
        self.assertEqual(day_arg['type'], 'IntegerArgument')
        self.assertEqual(day_arg['default'], None)
        self.assertEqual(day_arg['required'], False)

        # name arg
        name_arg = args['name']
        self.assertEqual(name_arg['description'],
                "The name for your datetime")
        self.assertEqual(name_arg['detailed_description'],
                "You can give your time a name, which will be returned back to you in the response, as the field `name`. If you omit this input parameter, your response won't include a `name`.")
        self.assertEqual(name_arg['type'], 'StringArgument')
        self.assertEqual(name_arg['default'], False)
        self.assertEqual(name_arg['required'], False)
        self.assertEqual(name_arg['min_length'], 3)
        self.assertEqual(name_arg['max_length'], 20)

        # include time
        incl_time = args['include_time']
        self.assertEqual(incl_time['description'],
                "Include the time in the output?")
        self.assertEqual(incl_time['detailed_description'],
                "If present, the response will include JSON fields for the current time, including `hours`, `minutes`, and `seconds`.")
        self.assertEqual(incl_time['type'], 'BooleanArgument')
        self.assertEqual(incl_time['default'], False)
        self.assertEqual(incl_time['required'], False)


        return_doc = current_time_doc['returns']
        self.assertEqual(return_doc['description'],
                "The DateTimeResource representation of the current time on the server.")
        self.assertEqual(return_doc['resource_name'], 'DateTime')
        self.assertEqual(return_doc['resource_type'], 'DateTimeResource')


    def validate_example_app_resource_doc (self, resource_dict):
        self.assertFalse(True)
