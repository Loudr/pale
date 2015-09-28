# -*- coding: utf-8 -*-
import unittest

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
