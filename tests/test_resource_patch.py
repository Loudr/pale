# -*- coding: utf-8 -*-
import unittest

from pale import Resource, ResourcePatch
from pale.fields import (BaseField, IntegerField, ListField, ResourceField,
        ResourceListField, StringField)


class Stats(object):
    def __init__(self):
        self.logins = 0


class StatsResource(Resource):
    _value_type = 'Test "stats" resource for patches'
    _underlying_model = Stats

    logins = IntegerField("Number of logins")


class User(object):
    def __init__(self, id, username):
        assert isinstance(username, basestring)
        self.username = username
        assert isinstance(id, basestring)
        self.id = id
        self.stats = Stats()


class UserResource(Resource):
    _value_type = 'Test "user" resource for patches'
    _underlying_model = User

    username = StringField("Username")
    id = StringField("User ID")
    stats = ResourceField("Test of a nested resource",
        resource_type=StatsResource)


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
            'stats': {
                'logins': 12
            }
        }

        user_resouce = UserResource()

        dt = user_resouce._render_serializable(user, None)
        self.assertEqual(dt['username'], 'soundofjw')
        self.assertEqual(dt['stats']['logins'], 0)

        patch = ResourcePatch(patch_data, user_resouce)

        patch.apply_to_model(user)
        dt = user_resouce._render_serializable(user, None)
        self.assertEqual(dt['username'], 'ammoses')
        self.assertEqual(dt['stats']['logins'], 12)


