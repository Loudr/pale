from __future__ import absolute_import
import logging
import webapp2

import pale

RESPONSE_CLASS = webapp2.Response


try:
    """webapp2 does not support the PATCH method at the time this code was
    written. This patch appends the PATCH method."""
    allowed_methods = webapp2.WSGIApplication.allowed_methods
    new_allowed_methods = allowed_methods.union(('PATCH',))
    webapp2.WSGIApplication.allowed_methods = new_allowed_methods
except Exception, exc:
    logging.warn("Failed to monkeypatch webapp2: %r", exc)

def pale_webapp2_request_handler_generator(pale_endpoint):
    """Generate a webapp2.RequestHandler class for the pale endpoint.

    webapp2 handles requests with subclasses of the RequestHandler class,
    instead of using functions like Flask, so we need to generate a new class
    for each pale endpoint.
    """
    def pale_handler(self, *args, **kwargs):
        return pale_endpoint._execute(self.request)
    cls = type(pale_endpoint._route_name,
            (webapp2.RequestHandler,),
            dict(pale_handler=pale_handler))
    return cls


def bind_pale_to_webapp2(pale_app_module,
        webapp_wsgiapplication,
        route_prefix=None):
    """Binds a Pale API implementation to a webapp2 WSGIApplication"""

    if not isinstance(webapp_wsgiapplication, webapp2.WSGIApplication):
        raise TypeError("pale.adapters.webapp2.bind_pale_to_webapp2 expected "
                "the passed in webapp_wsgiapplication to be an instance of "
                "WSGIApplication, but it was an instance of %s instead."
                % (type(webapp_wsgiapplication), ))

    if not pale.is_pale_module(pale_app_module):
        raise TypeError("pale.adapters.webapp2.bind_pale_to_webapp2 expected "
                "the passed in pale_app_module to be a Python module with a "
                "`_module_type` value equal to `pale.ImplementationModule`, "
                "but it found an instance of %s instead."
                % (type(pale_app_module), ))

    endpoints = pale.extract_endpoints(pale_app_module)

    for endpoint in endpoints:
        endpoint._set_response_class(RESPONSE_CLASS)
        method = endpoint._http_method
        name = endpoint._route_name

        req_handler = pale_webapp2_request_handler_generator(endpoint)

        route_uri = endpoint._uri
        if route_prefix is not None:
            route_uri = "%s%s" % (route_prefix, route_uri)

        route = webapp2.Route(
                route_uri,
                handler=req_handler,
                name=name,
                handler_method='pale_handler',
                methods=[method])
        webapp_wsgiapplication.router.add(route)


class DefaultWebapp2Context(pale.context.DefaultContext):

    def build_args_from_request(self, request):
        keys = request.arguments()
        req_args = {}

        for key in keys:
            req_args[key] = request.get_all(key)

        if request.content_type == 'application/json':
            json_args = request.json_body
            for k,v in json_args.iteritems():
                if k in req_args:
                    logging.warning("Found duplicate argument %s. "
                            "Preferring json argument to querystring arg.", k)
                req_args[k] = v

        # route args
        for k,v in request.route_kwargs.iteritems():
            if k in req_args:
                logging.warning("Found duplicate argument %s. "
                        "Preferring route argument to querystring and args.", k)
            req_args[k] = v
        return req_args

    def __init__(self, endpoint, request):
        super(DefaultWebapp2Context, self).__init__()
        self.headers = request.headers
        self.cookies = request.cookies
        self.request = request
        self.body = request.body
        self._raw_args = self.build_args_from_request(request)
        self.route_args = request.route_args
        self.route_kwargs = request.route_kwargs
        self.current_user = None
        self.endpoint = endpoint
