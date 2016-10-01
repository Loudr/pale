import json
import unittest
import inspect

from pale.doc import generate_doc_dict, generate_json_docs, generate_basic_type_docs, \
  document_endpoint, generate_raml_tree, generate_raml_resource_types, \
  generate_raml_resources, clean_description

COUNT_ENDPOINTS = 9
"""Number of endpoints we expect to find in example_app."""

class PaleDocTests(unittest.TestCase):
    def setUp(self):
        super(PaleDocTests, self).setUp()
        from tests.example_app import api as example_pale_app
        from pale import fields
        self.example_app = example_pale_app
        self.example_fields = fields
        self.doc_dict = generate_doc_dict(self.example_app)


    def test_doc_dict_root_structure(self):
        self.assertTrue('endpoints' in self.doc_dict)
        self.assertTrue(isinstance(self.doc_dict['endpoints'], dict))

        self.assertTrue('resources' in self.doc_dict)
        self.assertTrue(isinstance(self.doc_dict['resources'], dict))


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
        # we defined n endpoints in the example app
        self.assertEqual(len(endpoints), COUNT_ENDPOINTS)

        # the current time endpoint
        current_time_doc = endpoints['current_time']

        self.assertEqual(current_time_doc['uri'], '/time/current')
        self.assertEqual(current_time_doc['http_method'], 'GET')
        self.assertEqual(current_time_doc['arguments'], {})

        return_doc = current_time_doc['returns']
        self.assertEqual(return_doc['description'],
                "The DateTimeResource representation of the current time on the server.")
        self.assertEqual(return_doc['resource_name'], 'DateTime Resource')
        self.assertEqual(return_doc['resource_type'], 'DateTimeResource')


    def test_endpoint_with_args_docs(self):
        endpoints = self.doc_dict['endpoints']
        # we defined n endpoints in the example app
        self.assertEqual(len(endpoints), COUNT_ENDPOINTS)

        # the current time endpoint
        parse_time_doc = endpoints['parse_time']

        self.assertEqual(parse_time_doc['uri'], '/time/parse')
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


    def test_clean_description(self):
        """The descriptions need to be free of artifacts created by the documentation process.
        Also, any string that doesn't end with punctuation is given a period."""

        test_leading_spaces = clean_description("   Hey,")
        self.assertEquals(test_leading_spaces, "Hey,")
        test_multiple_spaces = clean_description("   look at this!")
        self.assertEquals(test_multiple_spaces, "look at this!")
        test_newlines = clean_description("\nsomeone left")
        self.assertEquals(test_newlines, "someone left.")
        test_colon = clean_description("this : sentence")
        self.assertEquals(test_colon, "this = sentence.")
        test_colon_url = clean_description("at https://loudr.fm")
        self.assertEquals(test_colon_url, "at https://loudr.fm.")
        test_machine_code = clean_description("(with code in it)<pale.fields.string.StringField object at 0x106edbed0>")
        self.assertEquals(test_machine_code, "(with code in it).")
        test_punctuation = clean_description("hanging")
        self.assertEquals(test_punctuation, "hanging.")


    def test_resource_doc(self):
        resources = self.doc_dict['resources']
        # we defined n resources in the example app
        self.assertEqual(len(resources), 3)

        resource = resources['DateTime Resource']
        self.assertEqual(resource['name'], 'DateTime Resource')
        self.assertEqual(resource['description'],
                'A simple datetime resource used for testing Pale Resources.')

        resource = resources['DateTime Range Resource']
        self.assertEqual(resource['name'], 'DateTime Range Resource')
        self.assertEqual(resource['description'],
                'A time range that returns some nested resources')


    def test_generate_basic_type_docs(self):
        fields = self.example_fields
        sample_existing_types = {
            "oauth_scope": {
                "description": "An existing oauth scope type",
                "type": "base"
            }
        }

        # set up basic fields the same way as generate_raml_docs
        basic_fields = []
        for field_module in inspect.getmembers(fields, inspect.ismodule):
            for field_class in inspect.getmembers(field_module[1], inspect.isclass):
                basic_fields.append(field_class[1])
        test_types = generate_basic_type_docs(basic_fields, sample_existing_types)[1]

        self.assertTrue(len(basic_fields) > 0)
        self.assertTrue(test_types.get('base') != None)
        self.assertEquals(test_types["base"]["type"], "object")
        self.assertEquals(test_types["list"]["type"], "array",
                "Sets type for children of RAML built-in types to their parent type")
        self.assertEquals(test_types.get("oauth_scope"), None,
                "Does not overwrite an existing type")


    def test_generate_raml_tree(self):
        # set up test_tree the same way as generate_raml_docs
        from pale import extract_endpoints, extract_resources, is_pale_module
        raml_resources = extract_endpoints(self.example_app)
        raml_resource_doc_flat = { ep._route_name: document_endpoint(ep) for ep in raml_resources }
        test_tree = generate_raml_tree(raml_resource_doc_flat, version="")

        # check if the tree is parsing the URIs correctly
        self.assertTrue(test_tree.get("path") != None)
        self.assertTrue(test_tree["path"]["time"] != None)
        self.assertTrue(test_tree["path"]["time"]["path"]["current"] != None)
        self.assertTrue(test_tree["path"]["arg_test/{arg_a}"] != None,
                "Includes parent folder in the path for URIs")
        self.assertTrue(test_tree["path"]["arg_test/{arg_a}"]["path"]["{arg_b}"] != None,
                "Correctly parses nested URIS")

        test_endpoint = test_tree["path"]["time"]["path"]["parse"]["endpoint"]

        # check if the endpoint contains what we expect
        self.assertEquals(test_endpoint["http_method"], "POST")
        self.assertEquals(test_endpoint["returns"]["resource_type"], "DateTimeResource")
        self.assertEquals(test_endpoint["arguments"]["month"]["min_value"], 1)


    def test_generate_raml_resource_types(self):
        test_types = generate_raml_resource_types(self.example_app)
        test_string = "day:\n        type: integer\n        description: The date of the month"
        self.assertTrue(test_string in test_types,
                "Contains some of the output we expect")
        self.assertTrue("affords\n" not in test_types,
                "Does not contain newlines in descriptions")


    def test_generate_raml_resources(self):

        # mock a user instance
        class User(object):
            def __init__(self, is_admin):
                self.is_admin = is_admin

        test_admin_user = User(True)
        test_public_user = User(False)
        test_resources_admin = generate_raml_resources(self.example_app, "", test_admin_user)
        test_string = "responses:\n      200:\n        body:\n          description: app resource."

        self.assertTrue(test_string in test_resources_admin,
                "Contains some of the output we expect")
        self.assertTrue("start time.\n" not in test_resources_admin,
                "Does not contain newlines in descriptions")
        self.assertTrue("<" not in test_resources_admin,
                """Does not contain the machine code version of string formatting, like
                '<pale.fields.string.StringField object at 0x1132bd2d0>'
                for example""")

        test_resources_public = generate_raml_resources(self.example_app, "", test_public_user)
        test_restricted_resource = "Include the time in the output?"

        self.assertTrue(test_restricted_resource not in test_resources_public,
                "Does not include restricted resources for public users")
        self.assertTrue(test_restricted_resource in test_resources_admin,
                "Does include restricted resources for admin users")
