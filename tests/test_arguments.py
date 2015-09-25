# -*- coding: utf-8 -*-
import unittest

from pale import Endpoint
from pale.arguments import (BaseArgument, BooleanArgument, FloatArgument,
        IntegerArgument, ListArgument, ScopeArgument, StringArgument,
        StringListArgument, URLArgument)


class ArgumentTests(unittest.TestCase):

    def expect_valid_argument(self, argument_class, value):
        pass

    def expect_invalid_argument(self, argument_class, value):
        pass


    def test_builtin_arguments(self):
        self.expect_valid_argument(BooleanArgument, 'true')
        self.expect_valid_argument(BooleanArgument, 'TRUE')
        self.expect_valid_argument(BooleanArgument, 'True')
        self.expect_valid_argument(BooleanArgument, 'TrUe')
        self.expect_valid_argument(BooleanArgument, 'false')
        self.expect_valid_argument(BooleanArgument, 'FALSE')
        self.expect_valid_argument(BooleanArgument, 'False')
        self.expect_valid_argument(BooleanArgument, 'FaLSe')



