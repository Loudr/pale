import json
import unittest

from pale.doc import generate_doc_dict, generate_json_docs

class PaleDocTests(unittest.TestCase):
    def setUp(self):
        super(PaleDocTests, self).setUp()
        from tests import example_app
        self.example_app = example_app
        self.doc_dict = generate_doc_dict(example_app)


    def test_doc_dict_root_structure(self):
        self.assertTrue('endpoints' in self.doc_dict)
        self.assertTrue(isinstance(self.doc_dict['endpoints'], dict))

        self.assertTrue('resources' in self.doc_dict)
        self.assertTrue(isinstance(self.doc_dict['resources'], list))


    def test_doc_json(self):
        json_docs = generate_json_docs(self.example_app)

        # use yaml's safe_load here, because it returns strings instead
        # of unicode, and we know that our test data doesn't have any
        # strictly-unicode characters.
        import yaml
        json_dict = yaml.safe_load(json_docs)
        self.assertDictEqual(json_dict, self.doc_dict)


    def test_endpoint_without_args_docs(self):
        endpoints = self.doc_dict['endpoints']
        # we defined two endpoints in the example app
        self.assertEqual(len(endpoints), 2)

        # the current time endpoint
        current_time_doc = endpoints['current_time']

        self.assertEqual(current_time_doc['uri'], '/current_time/')
        self.assertEqual(current_time_doc['http_method'], 'GET')
        self.assertEqual(current_time_doc['arguments'], {})

        return_doc = current_time_doc['returns']
        self.assertEqual(return_doc['description'],
                "The DateTimeResource representation of the current time on the server.")
        self.assertEqual(return_doc['resource_name'], 'DateTime Resource')
        self.assertEqual(return_doc['resource_type'], 'DateTimeResource')


    def test_endpoint_with_args_docs(self):
        endpoints = self.doc_dict['endpoints']
        # we defined two endpoints in the example app
        self.assertEqual(len(endpoints), 2)

        # the current time endpoint
        parse_time_doc = endpoints['parse_time']

        self.assertEqual(parse_time_doc['uri'], '/parse_time/')
        self.assertEqual(parse_time_doc['http_method'], 'POST')

        return_doc = parse_time_doc['returns']
        self.assertEqual(return_doc['description'],
                "The DateTimeResource corresponding to the timing information sent in by the requester.")
        self.assertEqual(return_doc['resource_name'], 'DateTime Resource')
        self.assertEqual(return_doc['resource_type'], 'DateTimeResource')

        args = parse_time_doc['arguments']
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
        self.assertEqual(month_arg['max_value'], 12)
        self.assertEqual(month_arg['required'], True)

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
        self.assertEqual(name_arg['default'], None)
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


    def test_resource_doc(self):
        resources = self.doc_dict['resources']
        # we only defined one resource in the example app
        self.assertEqual(len(resources), 1)

        resource = resources[0]
        self.assertEqual(resource['name'], 'DateTime Resource')
        self.assertEqual(resource['description'],
                'A simple datetime resource used for testing Pale Resources.')
