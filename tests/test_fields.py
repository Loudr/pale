import unittest

from pale.fields import BaseField, IntegerField, StringField

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
