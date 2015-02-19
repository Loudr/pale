import json
import re
import sys

from pale import extract_endpoints

def run_pale_doc():
  print "hello"


# this guy matches a single newline, but omits chunks of newlines strewn
# together, so that a string like "hi i am\nsome documentation\n\nhello"
# can be substituted to read "hi i am some documentation\n\nhello"
newline_substitution_regex = re.compile(r"(?<!\n)\n(?!\n)")


def generate_doc_dict(module):
    """Compile a Pale module's documentation into a python dictionary.

    The returned dictionary is suitable to be rendered by a JSON formatter,
    or passed to a template engine, or manipulated in some other way.
    """
    module_endpoints = extract_endpoints(module)

    ep_doc = { ep.name: extract_endpoint_doc(ep) for ep in module_endpoints }

    return {'endpoints': ep_doc}


def extract_endpoint_doc(endpoint):
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

    args = endpoint.arguments
    if args is None:
        return None
    return []


def format_endpoint_returns_doc(endpoint):
    """Return documentation about the resource that an endpoint returns."""
    description = py_doc_trim(endpoint.returns.description)
    return {
        'description': description,
        'resource_name': endpoint.returns.name,
        'resource_type': endpoint.returns.__class__.__name__
    }



def generate_json_docs(module):
    """Return a JSON string format of a Pale module's documentation.

    This string can either be printed out, written to a file, or piped to some
    other tool.

    This method is a shorthand for calling `generate_doc_dict` and passing
    it into a json serializer.
    """
    return json.dumps(generate_doc_dict(module))


def py_doc_trim(docstring):
    """Trim a python doc string.

    This example is nipped from https://www.python.org/dev/peps/pep-0257/,
    which describes how to conventionally format and trim docstrings.

    It has been modified to replace single newlines with a space, but leave
    multiple consecutive newlines in tact.
    """
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # The single string returned by the original function
    joined = '\n'.join(trimmed)
    # Return a version that replaces single newlines with spaces
    return newline_substitution_regex.sub(" ", joined)

