# -*- coding: utf-8 -*-
import unittest

from pale import Resource, ResourcePatch
from pale.fields import (BaseField, IntegerField, ListField, ResourceField,
        ResourceListField, StringField)

class User(object):
    def __init__(self, id, username):
        self.logins = 0
        assert isinstance(username, basestring)
        self.username = username
        assert isinstance(id, basestring)
        self.id = id


class UserResource(Resource):
    _value_type = 'Test "user" resource for patches'
    _underlying_model = User

    username = StringField("Username")
    logins = IntegerField("Number of logins")
    id = StringField("User ID")


class ResourcePatchTests(unittest.TestCase):

    def setUp(self):
        super(ResourcePatchTests, self).setUp()

    def test_patch_resource(self):

        user = User(
            id="001",
            username="soundofjw",
            )

        patch_data = {
            'username': 'ammoses',
            'logins': 12
        }

        user_resouce = UserResource()
        patch = ResourcePatch(patch_data, user_resouce)

        patch.apply_to_model(user)
        dt = user_resouce._render_serializable(user, None)
        self.assertEqual(dt['username'], 'ammoses')
        self.assertEqual(dt['logins'], 12)


