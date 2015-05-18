import argparse
import imp
import json

from pale.utils import py_doc_trim


def run_pale_doc():
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_pale_module')
    parser.add_argument('-p', '--pretty',
            help="pretty-print the json output",
            action='store_true')
    parser.add_argument('-n', '--print_newlines',
            help="output json with actual newlines instead of \\n characters",
            action='store_true')
    args = parser.parse_args()
    module_path = initify_module_path(args.path_to_pale_module)
    try:
        pale_module = imp.load_source('loaded_pale_implemntation',
                module_path)
    except Exception as e:
        print e
        return
    json_docs = generate_json_docs(pale_module, args.pretty)
    if args.print_newlines:
        json_docs = json_docs.replace('\\n', '\n')
    print json_docs


def initify_module_path(path):
    init = '__init__.py'
    if path.endswith(init):
        return path
    if not path.endswith('/'):
        path = path + '/'
    return path + init


def generate_json_docs(module, pretty_print=False):
    """Return a JSON string format of a Pale module's documentation.

    This string can either be printed out, written to a file, or piped to some
    other tool.

    This method is a shorthand for calling `generate_doc_dict` and passing
    it into a json serializer.
    """
    indent = None
    separators = (',', ':')
    if pretty_print:
        indent = 4
        separators = (',', ': ')

    module_doc_dict = generate_doc_dict(module)
    json_str = json.dumps(module_doc_dict,
            indent=indent,
            separators=separators)
    return json_str


def generate_doc_dict(module):
    """Compile a Pale module's documentation into a python dictionary.

    The returned dictionary is suitable to be rendered by a JSON formatter,
    or passed to a template engine, or manipulated in some other way.
    """
    from pale import extract_endpoints, extract_resources, is_pale_module
    if not is_pale_module(module):
        raise ValueError(
                """The passed in `module` (%s) is not a pale module. `paledoc`
                only works on modules with a `_module_type` set to equal
                `pale.ImplementationModule`.""")

    module_endpoints = extract_endpoints(module)
    ep_doc = { ep._route_name: document_endpoint(ep) for ep in module_endpoints }

    module_resources = extract_resources(module)
    res_doc = [document_resource(r) for r in module_resources]

    return {'endpoints': ep_doc,
            'resources': res_doc}


def document_endpoint(endpoint):
    """Extract the full documentation dictionary from the endpoint."""
    descr = py_doc_trim(endpoint.__doc__)
    docs = {
        'name': endpoint._route_name,
        'http_method': endpoint._http_method,
        'uri': endpoint._uri,
        'description': descr,
        'arguments': extract_endpoint_arguments(endpoint),
        'returns': format_endpoint_returns_doc(endpoint)
    }
    return docs


def extract_endpoint_arguments(endpoint):
    """Extract the argument documentation from the endpoint."""

    ep_args = endpoint._arguments
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
    description = py_doc_trim(endpoint._returns._description)
    return {
        'description': description,
        'resource_name': endpoint._returns._value_type,
        'resource_type': endpoint._returns.__class__.__name__
    }


def document_resource(resource):
    field_doc = { name: field.doc_dict() for name, field \
            in resource._fields.iteritems() }

    res_doc = {
        'name': resource._value_type,
        'description': py_doc_trim(resource.__doc__),
        'fields': field_doc,
        'default_fields': list(resource._default_fields)
    }
    return res_doc
