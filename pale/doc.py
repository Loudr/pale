import argparse
import imp
import json

from pale import extract_endpoints, extract_resources
from pale.utils import py_doc_trim



def run_pale_doc():
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_pale_module')
    args = parser.parse_args()
    module_path = initify_module_path(args.path_to_pale_module)
    try:
        pale_module = imp.load_source('paledoc.loaded_implemntation',
                module_path)
    except Exception as e:
        print e
        return
    print generate_json_docs(pale_module)


def initify_module_path(path):
    init = '__init__.py'
    if path.endswith(init):
        return path
    if not path.endswith('/'):
        path = path + '/'
    return path + init


def generate_json_docs(module):
    """Return a JSON string format of a Pale module's documentation.

    This string can either be printed out, written to a file, or piped to some
    other tool.

    This method is a shorthand for calling `generate_doc_dict` and passing
    it into a json serializer.
    """
    return json.dumps(generate_doc_dict(module))


def generate_doc_dict(module):
    """Compile a Pale module's documentation into a python dictionary.

    The returned dictionary is suitable to be rendered by a JSON formatter,
    or passed to a template engine, or manipulated in some other way.
    """
    module_endpoints = extract_endpoints(module)
    ep_doc = { ep.name: document_endpoint(ep) for ep in module_endpoints }

    module_resources = extract_resources(module)
    res_doc = [document_resource(r) for r in module_resources]

    return {'endpoints': ep_doc,
            'resources': res_doc}


def document_endpoint(endpoint):
    """Extract the full documentation dictionary from the endpoint."""
    descr = py_doc_trim(endpoint.__doc__)
    docs = {
        'name': endpoint.name,
        'http_method': endpoint.method,
        'uri': endpoint.uri,
        'description': descr,
        'arguments': extract_endpoint_arguments(endpoint),
        'returns': format_endpoint_returns_doc(endpoint)
    }
    return docs


def extract_endpoint_arguments(endpoint):
    """Extract the argument documentation from the endpoint."""

    ep_args = endpoint.arguments
    if ep_args is None:
        return None

    arg_docs = { k: format_endpoint_argument_doc(a) \
            for k, a in ep_args.iteritems() }
    return arg_docs


def format_endpoint_argument_doc(argument):
    """Return documentation about the argument that an endpoint accepts."""
    doc = argument.doc_dict()

    # Trim the strings a bit
    doc['description'] = py_doc_trim(doc['description'])
    details = doc.get('detailed_description', None)
    if details is not None:
        doc['detailed_description'] = py_doc_trim(details)

    return doc


def format_endpoint_returns_doc(endpoint):
    """Return documentation about the resource that an endpoint returns."""
    description = py_doc_trim(endpoint.returns.description)
    return {
        'description': description,
        'resource_name': endpoint.returns.name,
        'resource_type': endpoint.returns.__class__.__name__
    }


def document_resource(resource):
    return {
        'name': resource.name,
        'description': py_doc_trim(resource.__doc__)
    }
