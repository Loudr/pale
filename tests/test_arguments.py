# -*- coding: utf-8 -*-
import unittest
import urlparse

from pale import Endpoint
from pale.arguments import (BaseArgument, BooleanArgument, FloatArgument,
        IntegerArgument, ListArgument, ScopeArgument, StringArgument,
        StringListArgument, URLArgument)
from pale.errors import ArgumentError


class ArgumentTests(unittest.TestCase):

    def expect_valid_argument(self, arg_inst, value, expected):
        validated = arg_inst.validate(value, 'test item')
        self.assertEqual(validated, expected)

    def expect_invalid_argument(self, arg_inst, value):
        with self.assertRaises(ArgumentError):
            validated = arg_inst.validate(value, 'test item')


    def test_boolean_arguments(self):
        required_bool_arg = BooleanArgument('test bool arg', required=True)
        self.expect_valid_argument(required_bool_arg, 'true', True)
        self.expect_valid_argument(required_bool_arg, 'TRUE', True)
        self.expect_valid_argument(required_bool_arg, 'True', True)
        self.expect_valid_argument(required_bool_arg, 'TrUe', True)
        self.expect_valid_argument(required_bool_arg, 'false', False)
        self.expect_valid_argument(required_bool_arg, 'FALSE', False)
        self.expect_valid_argument(required_bool_arg, 'False', False)
        self.expect_valid_argument(required_bool_arg, 'FaLSe', False)
        self.expect_invalid_argument(required_bool_arg, None)
        self.expect_invalid_argument(required_bool_arg, 'hello')

        # allow 0/1 integers, but not other ints
        self.expect_valid_argument(required_bool_arg, '0', False)
        self.expect_valid_argument(required_bool_arg, '1', True)
        self.expect_invalid_argument(required_bool_arg, '-241')
        self.expect_invalid_argument(required_bool_arg, '241')
        self.expect_invalid_argument(required_bool_arg, '0.0')
        self.expect_invalid_argument(required_bool_arg, '1.0')
        self.expect_invalid_argument(required_bool_arg, '1.234')

        optional_bool_arg = BooleanArgument('test arg', required=False)
        self.expect_valid_argument(optional_bool_arg, 'True', True)
        self.expect_valid_argument(optional_bool_arg, None, None)

        default_bool_arg = BooleanArgument('test arg',
                                           required=False,
                                           default=False)
        self.expect_valid_argument(default_bool_arg, None, False)
        # passing a value overrides the default
        self.expect_valid_argument(default_bool_arg, 'true', True)

        required_default_bool_arg = BooleanArgument('test arg',
                                                    required=True,
                                                    default=False)
        self.expect_valid_argument(required_default_bool_arg, None, False)
        self.expect_valid_argument(required_default_bool_arg, 'true', True)


    def test_string_arguments(self):
        # damn near everything will probably come in as a string, so there's
        # only so much to test without regex matching
        required_string_arg = StringArgument('test string arg', required=True)
        self.expect_valid_argument(required_string_arg,
                'hello, world', 'hello, world')
        self.expect_valid_argument(required_string_arg,
                '12345', '12345')
        self.expect_invalid_argument(required_string_arg, None)
        self.expect_invalid_argument(required_string_arg, '')

        optional_string_arg = StringArgument('test string arg', required=False)
        self.expect_valid_argument(optional_string_arg,
                'hello, world', 'hello, world')
        self.expect_valid_argument(optional_string_arg, None, None)

        default_string_arg = StringArgument('test string arg',
                required=False, default="hello tests")
        self.expect_valid_argument(default_string_arg,
                'hello, world', 'hello, world')
        self.expect_valid_argument(default_string_arg, None, 'hello tests')

        required_default_string_arg = StringArgument('test string arg',
                required=True, default="hello tests")
        self.expect_valid_argument(required_default_string_arg,
                'hello, world', 'hello, world')
        self.expect_valid_argument(required_default_string_arg,
                None, 'hello tests')


    def test_url_arguments(self):
        required_url_arg = URLArgument('test url arg', required=True)
        google_url = urlparse.urlparse('https://www.google.com/')
        ftp_url = urlparse.urlparse('ftp://www.google.com/')
        url_path = urlparse.urlparse('/foo/bar/baz')
        url_path_with_query = urlparse.urlparse('/foo/bar/baz?query=hi')
        url_path_with_fragment = urlparse.urlparse('/foo/bar/baz#hello')
        url_path_with_query_fragment = urlparse.urlparse(
                '/foo/bar/baz?query=hi#hello')

        self.expect_invalid_argument(required_url_arg, None)
        self.expect_invalid_argument(required_url_arg, '')
        self.expect_invalid_argument(required_url_arg, ftp_url.geturl())
        self.expect_invalid_argument(required_url_arg, 'i am not a url')
        self.expect_invalid_argument(required_url_arg, url_path.geturl())
        self.expect_valid_argument(required_url_arg, google_url.geturl(),
                google_url)

        optional_url_arg = URLArgument('test string arg', required=False)
        self.expect_valid_argument(optional_url_arg, None, None)
        self.expect_valid_argument(optional_url_arg,
                google_url.geturl(), google_url)

        url_path_arg = URLArgument('test string arg', path_only=True)
        self.expect_invalid_argument(url_path_arg, google_url.geturl())
        self.expect_valid_argument(url_path_arg, url_path.geturl(),
                url_path)
        self.expect_valid_argument(url_path_arg,
                url_path_with_query.geturl(), url_path_with_query)
        self.expect_valid_argument(url_path_arg,
                url_path_with_fragment.geturl(), url_path_with_fragment)
        self.expect_valid_argument(url_path_arg,
                url_path_with_query_fragment.geturl(),
                url_path_with_query_fragment)


    def test_integer_arguments(self):
        required_int_arg = IntegerArgument('test integer arg', required=True)
        self.expect_invalid_argument(required_int_arg, 'i am not an int')
        # single characters aren't accidentally converted to ascii values
        self.expect_invalid_argument(required_int_arg, 'Q')
        self.expect_invalid_argument(required_int_arg, None)
        self.expect_valid_argument(required_int_arg, '123', 123)
        # no floats
        self.expect_invalid_argument(required_int_arg, '123.45')
        self.expect_valid_argument(required_int_arg, '-159', -159)

        optional_int_arg = IntegerArgument('test integer arg')
        self.expect_invalid_argument(optional_int_arg, 'i am not an int')
        self.expect_valid_argument(optional_int_arg, None, None)
        self.expect_valid_argument(optional_int_arg, '75', 75)

        default_int_arg = IntegerArgument('test integer arg', default=42)
        self.expect_invalid_argument(default_int_arg, 'i am not an int')
        self.expect_valid_argument(default_int_arg, None, 42)
        self.expect_valid_argument(default_int_arg, '33', 33)

        default_required_int_arg = IntegerArgument('test integer arg',
                default=42, required=True)
        self.expect_invalid_argument(default_required_int_arg,
                'i am not an int')
        self.expect_valid_argument(default_required_int_arg, None, 42)
        self.expect_valid_argument(default_required_int_arg, '33', 33)
        self.expect_valid_argument(default_required_int_arg, '0', 0)

        minimum_int_arg = IntegerArgument('test integer arg', min_value=9)
        self.expect_invalid_argument(minimum_int_arg, 'i am not an int')
        self.expect_invalid_argument(minimum_int_arg, 8)
        self.expect_invalid_argument(minimum_int_arg, -873)
        self.expect_valid_argument(minimum_int_arg, 9, 9)
        self.expect_valid_argument(minimum_int_arg, 31423, 31423)

        maximum_int_arg = IntegerArgument('test integer arg', max_value=9)
        self.expect_invalid_argument(maximum_int_arg, 'i am not an int')
        self.expect_invalid_argument(maximum_int_arg, 10)
        self.expect_invalid_argument(maximum_int_arg, 873)
        self.expect_valid_argument(maximum_int_arg, 9, 9)
        self.expect_valid_argument(maximum_int_arg, -31423, -31423)

        min_max_int_arg = IntegerArgument('test integer arg',
                min_value=0, max_value=9)
        self.expect_invalid_argument(min_max_int_arg, 'i am not an int')
        self.expect_invalid_argument(min_max_int_arg, 10)
        self.expect_invalid_argument(min_max_int_arg, 873)
        self.expect_invalid_argument(min_max_int_arg, -1)
        self.expect_invalid_argument(min_max_int_arg, -972151)
        self.expect_valid_argument(min_max_int_arg, 9, 9)
        self.expect_valid_argument(min_max_int_arg, 0, 0)
        self.expect_valid_argument(min_max_int_arg, 5, 5)


    def test_float_arguments(self):
        required_float_arg = FloatArgument('test float arg', required=True)
        self.expect_invalid_argument(required_float_arg, 'i am not a float')
        # single characters aren't accidentally converted to ascii values
        self.expect_invalid_argument(required_float_arg, 'Q')
        self.expect_invalid_argument(required_float_arg, None)
        self.expect_valid_argument(required_float_arg, '123', 123.0)
        self.expect_valid_argument(required_float_arg, '123.45', 123.45)
        self.expect_valid_argument(required_float_arg, '-159', -159.0)

        optional_float_arg = FloatArgument('test float arg')
        self.expect_invalid_argument(optional_float_arg, 'i am not a float')
        self.expect_valid_argument(optional_float_arg, None, None)
        self.expect_valid_argument(optional_float_arg, '3.14159', 3.14159)

        default_float_arg = FloatArgument('test float arg', default=1.5)
        self.expect_invalid_argument(default_float_arg, 'i am not a float')
        self.expect_valid_argument(default_float_arg, None, 1.5)
        self.expect_valid_argument(default_float_arg, 42.245, 42.245)

        min_float_arg = FloatArgument('test float arg', min_value=0.2)
        self.expect_invalid_argument(min_float_arg, 'i am not a float')
        self.expect_invalid_argument(min_float_arg, '-1.589')
        self.expect_invalid_argument(min_float_arg, '0.1')
        self.expect_valid_argument(min_float_arg, '0.2', 0.2)
        self.expect_valid_argument(min_float_arg, '12.245', 12.245)

        max_float_arg = FloatArgument('test float arg', max_value=100.0)
        self.expect_invalid_argument(max_float_arg, 'i am not a float')
        self.expect_invalid_argument(max_float_arg, '158.9')
        self.expect_invalid_argument(max_float_arg, '100.1')
        self.expect_valid_argument(max_float_arg, '0.1', 0.1)
        self.expect_valid_argument(max_float_arg, '99.9', 99.9)
        self.expect_valid_argument(max_float_arg, '-102.245', -102.245)

        min_max_float_arg = FloatArgument('test float arg',
                min_value=0.0, max_value=1.0)
        self.expect_invalid_argument(min_max_float_arg, 'i am not a float')
        self.expect_invalid_argument(min_max_float_arg, '1.1')
        self.expect_invalid_argument(min_max_float_arg, '-102.245')
        self.expect_invalid_argument(min_max_float_arg, '99.9')
        self.expect_valid_argument(min_max_float_arg, '0.1', 0.1)
        self.expect_valid_argument(min_max_float_arg, '0.567235', 0.567235)
        self.expect_valid_argument(min_max_float_arg, '0', 0.0)
        self.expect_valid_argument(min_max_float_arg, '1', 1.0)


    def test_scope_argument(self):
        required_scope_arg = ScopeArgument('test scope arg', required=True)
        self.expect_invalid_argument(required_scope_arg, None)
        self.expect_valid_argument(required_scope_arg, "hello world",
                ['hello', 'world'])
        self.expect_valid_argument(required_scope_arg,
                "hello.world and.goodbye.mars",
                ['hello.world', 'and.goodbye.mars'])


    def test_string_list_argument(self):
        comma_separated_string_list = StringListArgument('test string list arg',
                separator=',',
                trim_whitespace=False,
                required=True)
        self.expect_invalid_argument(comma_separated_string_list, None)
        self.expect_valid_argument(comma_separated_string_list, "hello world",
                ['hello world'])
        self.expect_valid_argument(comma_separated_string_list, "hello,world",
                ['hello', 'world'])
        self.expect_valid_argument(comma_separated_string_list, "hello, world",
                ['hello', ' world'])

        # it can also handle querystring lists, in which case, it'll get a list
        # directly, rather than a value-separated string
        self.expect_valid_argument(comma_separated_string_list,
                ['hello', 'world'],
                ['hello', 'world'])
        self.expect_valid_argument(comma_separated_string_list,
                ['hello', ' world'],
                ['hello', ' world'])

        comma_separated_string_list.trim_whitespace = True
        self.expect_valid_argument(comma_separated_string_list, "hello, world",
                ['hello', 'world'])
        self.expect_valid_argument(comma_separated_string_list,
                ['hello', 'world'],
                ['hello', 'world'])
        self.expect_valid_argument(comma_separated_string_list,
                ['hello', ' world'],
                ['hello', 'world'])
