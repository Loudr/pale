# -*- coding: utf-8 -*-

class DefaultContext(object):
    """A default Context object for pale request data"""
    def __init__(self):
        self.request = None
        self.headers = None
        self.cookies = None

        self.api_version = None

        self._raw_args = None
        self.args = None
        self.route_args = None

        self.current_user = None

        self.handler_result = None
        self.response = None
