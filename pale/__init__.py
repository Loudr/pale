import inspect
import types

from . import adapters
from . import arguments
from . import config
from . import context
from . import doc
from .endpoint import Endpoint
from .resource import NoContentResource, Resource, ResourceList

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

    classes = [v for (k,v) in inspect.getmembers(api_module.endpoints,
                                                 inspect.isclass)]
    instances = []

    for cls in classes:
        if Endpoint in cls.__bases__:
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
