import logging
import json

json_decoder = json.JSONDecoder()

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

    @classmethod
    def deserialize_args_from_body(cls, body):
        """Deserializes a JSON body into a dictionary of arguments."""

        if not body:
            return {}

        # Add arguments from json body
        try:
            j_args = json_decoder.decode(body)
            return j_args
        except:
            logging.exception(
                "Failed to parse arguments from JSON body.\n%s",
                body)
            return {}