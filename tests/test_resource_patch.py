# -*- coding: utf-8 -*-
import unittest

from pale import Resource, ResourcePatch
from pale.fields import (BaseField, IntegerField, ListField, ResourceField,
        ResourceListField, StringField)


class Stats(object):
    def __init__(self):
        self.logins = 0


class Counter(object):
    def __init__(self, key, value=0):
        self.key = key
        self.value = value


class StatsResource(Resource):
    _value_type = 'Test "stats" resource for patches'
    _underlying_model = Stats

    logins = IntegerField("Number of logins")


class CounterResource(Resource):
    _value_type = 'Test repeated nested resources'
    _underlying_model = Counter

    name = StringField("Name of counter",
        property_name='key')
    value = IntegerField("Value of counter")


class User(object):
    """Has:
    tokens - list of strings
    counters - list of Counter
    id - string id
    username - string username
    """
    def __init__(self, id, username):
        assert isinstance(username, basestring)
        self.username = username
        assert isinstance(id, basestring)
        self.id = id
        self.stats = Stats()
        self.counters = []
        self.tokens = []


class UserResource(Resource):
    _value_type = 'Test "user" resource for patches'
    _underlying_model = User

    username = StringField("Username")
    id = StringField("User ID")
    stats = ResourceField("Test of a nested resource",
        resource_type=StatsResource)

    counters = ResourceListField("List of misc. counters",
        resource_type=CounterResource)

    tokens = ListField("List of string tokens",
        item_type=StringField)


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
            },
            'counters': [
                {'name': 'products', 'value': 36}
            ],
            'tokens': [
                'gold-coin'
            ],
            'bad_field': True,
        }

        user_resouce = UserResource()

        dt = user_resouce._render_serializable(user, None)
        self.assertEqual(dt['username'], 'soundofjw')
        self.assertEqual(dt['stats']['logins'], 0)
        self.assertEqual(dt['counters'], [])
        self.assertEqual(dt['tokens'], [])

        patch = ResourcePatch(patch_data, user_resouce)
        patch.ignore_missing_fields = True

        patch.apply_to_model(user)

        dt = user_resouce._render_serializable(user, None)
        self.assertEqual(dt['username'], 'ammoses')
        self.assertEqual(dt['stats']['logins'], 12)
        self.assertEqual(dt['counters'][0], {'name': 'products', 'value': 36})
        self.assertEqual(dt['tokens'][0], 'gold-coin')

