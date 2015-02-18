import inspect
import types

import adapters
import arguments
import config
import context
from endpoint import Endpoint
from resource import NoContentResource, Resource, ResourceList

ImplementationModule = "_pale__api_implementation"

def is_pale_module(obj):
    is_it = isinstance(obj, types.ModuleType) and \
            hasattr(obj, '_module_type') and \
            obj._module_type == ImplementationModule
    return is_it


def extract_endpoints(api_module):
    """Iterates through an api implementation module to extract and instantiate
    endpoint objects to be passed to the HTTP-layer's router.
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
