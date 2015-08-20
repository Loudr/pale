# -*- coding: utf-8 -*-

"""Pale is an HTTP API specification tool for Flask and webapp2."""

import inspect
import types

from . import adapters
from . import arguments
from . import config
from . import context
from . import doc
from .endpoint import Endpoint
from .resource import NoContentResource, Resource, ResourceList

with open(path.join(path.dirname(__file__), 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

ImplementationModule = "_pale__api_implementation"

def is_pale_module(obj):
    is_it = isinstance(obj, types.ModuleType) and \
            hasattr(obj, '_module_type') and \
            obj._module_type == ImplementationModule
    return is_it


def extract_endpoints(api_module):
    """Return the endpoints from an API implementation module.

    The results returned by this are used to populate your HTTP layer's
    route handler, as well as by the documentation generator.
    """
    if not hasattr(api_module, 'endpoints'):
        raise ValueError(("pale.extract_endpoints expected the passed in "
            "api_module to have an `endpoints` attribute, but it didn't!"))

    endpoints = api_module.endpoints
    if isinstance(endpoints, types.ModuleType):
        classes = [v for (k,v) in inspect.getmembers(endpoints,
                                                     inspect.isclass)]
    elif isinstance(endpoints, (list, tuple)):
        classes = endpoints
    else:
        raise ValueError("Endpoints is not a module or list type!")

    instances = []

    for cls in classes:
        if cls != Endpoint and Endpoint in inspect.getmro(cls):
            instances.append(cls())
    return instances

def extract_resources(api_module):
    """Return the resources from an API implementation module.

    The results returned here are used to generate documentation.  They aren't
    currently used for anything in production.
    """
    endpoints = extract_endpoints(api_module)
    resource_classes = [ e._returns.__class__ for e in endpoints ]

    return list(set(resource_classes))
