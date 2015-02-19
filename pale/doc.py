import json

def run_pale_doc():
  print "hello"


def generate_doc_dict(module):
    """Compiles the documentation from a module into a dictionary suitable
    to be rendered to JSON, or to some other format, or passed to a template
    engine."""

    return {}

def generate_json_docs(module):
    """Returns the generated documentation, which you might like to print
    out directly, write to a file, or pipe to some other tool.
    """
    return json.dumps(generate_doc_dict(module))
