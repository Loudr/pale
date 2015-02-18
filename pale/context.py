class DefaultContext(object):
    """A default Context object for pale request data"""
    request = None
    headers = None
    cookies = None

    api_version = None

    _raw_args = None
    args = None
    route_args = None

    current_user = None

    handler_result = None
    response = None
