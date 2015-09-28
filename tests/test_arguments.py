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
