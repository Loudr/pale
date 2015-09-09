from __future__ import absolute_import
import flask
from flask import Blueprint

import pale


RESPONSE_CLASS = flask.Response

class ContextualizedHandler(object):
    """Flask route functions get called with no arguments unless there are
    arguments specified in the route path.  This contextualizer object wraps
    the desired pale executor by grabbing the flask request and populating the
    appropriate kwargs before passing them onto the execute function.
    """
    def __init__(self, func):
        self.handler = func

    def __call__(self, *args, **kwargs):
        """Call the handler with the flask request.

        We ignore the kwargs here, since they're also present on the request
        object as `request.view_args`.
        """
        request = flask.request
        return self.handler(request)


def bind_blueprint(pale_api_module, flask_blueprint):
    """Binds an implemented pale API module to a Flask Blueprint."""

    if not isinstance(flask_blueprint, Blueprint):
        raise TypeError(("pale.flask_adapter.bind_blueprint expected the "
                         "passed in flask_blueprint to be an instance of "
                         "Blueprint, but it was an instance of %s instead.")
                        % (type(flask_blueprint),))

    if not pale.is_pale_module(pale_api_module):
        raise TypeError(("pale.flask_adapter.bind_blueprint expected the "
                         "passed in pale_api_module to be a module, and to "
                         "have a _module_type defined to equal "
                         "pale.ImplementationModule, but it was an instance of "
                         "%s instead.")
                        % (type(pale_api_module),))

    endpoints = pale.extract_endpoints(pale_api_module)

    for endpoint in endpoints:
        endpoint._set_response_class(RESPONSE_CLASS)
        method = [endpoint._http_method]
        name = endpoint._route_name
        handler = endpoint._execute

        flask_blueprint.add_url_rule(
                endpoint._uri,
                name,
                view_func=ContextualizedHandler(handler),
                methods=method)


class DefaultFlaskContext(pale.context.DefaultContext):

    def build_args_from_request(self, request):
        body = request.get_data(as_text=True)

        qs_args = request.values.to_dict(flat=False)
        js_args = self.deserialize_args_from_body(body)

        qs_args.update(js_args)
        return qs_args

    def __init__(self, endpoint, request):
        super(DefaultFlaskContext, self).__init__()
        self.headers = request.headers
        self.cookies = request.cookies
        self.request = request
        self._raw_args = self.build_args_from_request(request)
        self.route_args = request.view_args
        self.current_user = None
        self.endpoint = endpoint

