# -*- coding: utf-8 -*-
import unittest

from pale import Resource
from pale.fields import (BaseField, IntegerField, ListField, ResourceField,
        ResourceListField, StringField)

from tests.example_app.api.resources import DateTimeResource


class FieldsTests(unittest.TestCase):

    def setUp(self):
        super(FieldsTests, self).setUp()


    def test_create_base_field(self):
        field = BaseField("integer",
                "This is a test field",
                "This is where I put special notes about the field")

        self.assertEqual(field.value_type, "integer")
        self.assertEqual(field.description, "This is a test field")
        self.assertEqual(field.details,
                "This is where I put special notes about the field")

        doc = field.doc_dict()
        self.assertEqual(doc["type"], "integer")
        self.assertEqual(doc["description"], "This is a test field")
        self.assertEqual(doc["extended_description"],
                "This is where I put special notes about the field")

        # test details default
        field = BaseField("integer",
                "This is a test field")
        self.assertIsNone(field.details)
        doc = field.doc_dict()
        self.assertIsNone(doc["extended_description"])


    def test_create_string_field(self):
        field = StringField("Your name",
                "You should expect a real name here, not some mish-mosh")
        self.assertEqual(field.value_type, "string")
        self.assertEqual(field.description, "Your name")
        self.assertEqual(field.details,
                "You should expect a real name here, not some mish-mosh")

        doc = field.doc_dict()
        self.assertEqual(doc["type"], "string")
        self.assertEqual(doc["description"], "Your name")
        self.assertEqual(doc["extended_description"],
                "You should expect a real name here, not some mish-mosh")

        field = StringField("Your name")
        self.assertIsNone(field.details)
        doc = field.doc_dict()
        self.assertIsNone(doc["extended_description"])


    def test_integer_field(self):
        field = IntegerField("The amount of stuff for your things",
                "This amount will always be a positive integer, but may "
                "be only eventually consistent.")

        self.assertEqual(field.value_type, "integer")
        self.assertEqual(field.description,
                "The amount of stuff for your things")
        self.assertEqual(field.details,
                "This amount will always be a positive integer, but may "
                "be only eventually consistent.")

        doc = field.doc_dict()
        self.assertEqual(doc["type"], "integer")
        self.assertEqual(doc["description"],
                "The amount of stuff for your things")
        self.assertEqual(doc["extended_description"],
                "This amount will always be a positive integer, but may "
                "be only eventually consistent.")

        field = IntegerField("Some amount thing")
        self.assertIsNone(field.details)
        doc = field.doc_dict()
        self.assertIsNone(doc["extended_description"])


    def test_list_field_with_no_item_type(self):
        list_no_item_type = ListField("This is a test list field",
                "You might add information about the list here.")
        self.assertEqual(list_no_item_type.value_type, "list")
        self.assertEqual(list_no_item_type.description,
                "This is a test list field")
        self.assertEqual(list_no_item_type.details,
                "You might add information about the list here.")
        self.assertEqual(list_no_item_type.item_type, BaseField)


    def test_create_list_field(self):
        field = ListField("This is a test list field",
                "You might add information about the list here.",
                item_type=StringField)
        self.assertEqual(field.value_type, "list")
        self.assertEqual(field.description,
                "This is a test list field")
        self.assertEqual(field.details,
                "You might add information about the list here.")
        self.assertEqual(field.item_type, StringField)

        doc = field.doc_dict()
        self.assertEqual(doc["type"], "list")
        self.assertEqual(doc["description"], "This is a test list field")
        self.assertEqual(doc["extended_description"],
                "You might add information about the list here.")
        self.assertEqual(doc["item_type"],
                StringField.value_type)


    def test_resource_field(self):
        """Test ResourceField creation and documentation
        
        A resource field is the primary way to nest objects.

        At a high level, a Resource is basically just a format and
        content specification for a JSON object, so if one of the values
        in that object is itself another object, it makes sense to
        specify the nested object as simply a nested resource.
        """
        field = ResourceField("This is a test resource field",
                "Why does this Resource have another Resource?",
                resource_type=DateTimeResource)

        self.assertEqual(field.value_type, "resource")
        self.assertEqual(field.description,
                "This is a test resource field")
        self.assertEqual(field.details,
                "Why does this Resource have another Resource?")
        self.assertEqual(field.resource_type, DateTimeResource)
        self.assertEqual(field.subfields, DateTimeResource._default_fields)

        doc = field.doc_dict()
        self.assertEqual(doc["type"], "resource")
        self.assertEqual(doc["description"], "This is a test resource field")
        self.assertEqual(doc["extended_description"],
                "Why does this Resource have another Resource?")
        self.assertEqual(doc["resource_type"],
                DateTimeResource._value_type)
        self.assertEqual(doc["default_fields"],
                field.subfields)


    def test_resource_field_no_type(self):
        field = ResourceField("This is a test resource field",
                "Why does this Resource have another Resource?")

        self.assertEqual(field.value_type, "resource")
        self.assertEqual(field.description,
                "This is a test resource field")
        self.assertEqual(field.details,
                "Why does this Resource have another Resource?")
        self.assertEqual(field.resource_type, Resource)
        self.assertEqual(field.subfields, None)
