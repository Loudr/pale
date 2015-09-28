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
        self.assertIsNotNone(validated)
        self.assertEqual(validated, expected)

    def expect_invalid_argument(self, arg_inst, value):
        with self.assertRaises(ArgumentError):
            validated = arg_inst.validate(value, 'test item')


    def test_boolean_arguments(self):
        required_bool_arg = BooleanArgument('test arg', required=True)
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
