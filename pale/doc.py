import argparse
import imp
import json
import re
import inspect
from collections import OrderedDict

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from pale.utils import py_doc_trim

# this will be useful in removing newlines and leading whitespace from descriptions
description_compiler = re.compile(r"\n\s*")

# this will be useful in replacing colons in descriptions
colon_compiler = re.compile(r":")

# this will be useful in removing things like:
#   <pale.fields.string.StringField object at 0x106edbed0>
# from descriptions
string_format_compiler = re.compile(r"(<.+>)")

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


def generate_raml_docs(module, fields, shared_types, title="My API", version="v1", base_uri="http://mysite.com/{version}"):
    """Return a RAML file of a Pale module's documentation as a string.

    The arguments for 'title', 'version', and 'base_uri' are added to the RAML header info.
    """
    output = StringIO()

    # Add the RAML header info
    output.write('#%RAML 1.0 \n')
    output.write('title: ' + title + ' \n')
    output.write('baseUri: ' + base_uri + ' \n')
    output.write('version: ' + version + '\n')
    output.write('mediaType: application/json\n\n')

    output.write("###############\n# Resource Types:\n###############\n\n")
    output.write('types:\n')

    basic_fields = []

    for field_module in inspect.getmembers(fields, inspect.ismodule):
        for field_class in inspect.getmembers(field_module[1], inspect.isclass):
            basic_fields.append(field_class[1])

    pale_basic_types = generate_basic_type_docs(basic_fields, {})

    output.write("\n# Pale Basic Types:\n\n")
    output.write(pale_basic_types[0])


    shared_fields = []

    for shared_type in shared_types:

        for field_class in inspect.getmembers(shared_type, inspect.isclass):

            shared_fields.append(field_class[1])

    pale_shared_types = generate_basic_type_docs(shared_fields, pale_basic_types[1])
    output.write("\n# Pale Shared Types:\n\n")
    output.write(pale_shared_types[0])


    raml_resource_types = generate_raml_resource_types(module)
    output.write("\n# API Resource Types:\n\n")
    output.write(raml_resource_types)

    raml_resources = generate_raml_resources(module, version)
    output.write("\n\n###############\n# API Endpoints:\n###############\n\n")
    output.write(raml_resources)

    raml_docs = output.getvalue()
    output.close()

    return raml_docs


def generate_type_docs(types):
    """Parse an object of types and generate RAML documentation for them.
    Expects each type to be either a regular type or a list/array. If a type is a list,
    it must specify what type to use for each item.
    """
    output = StringIO()

    indent = "  "  # 2

    # loop through the basic types and add them to the RAML formatted output
    for type_name in types:

        if types[type_name].get("type") != None:

            output.write(indent + type_name + ":\n")

            indent += "  "  # 4

            type_safe = types[type_name]["type"].replace(" ", "_")

            # if we are dealing with a list, set type to array and specify type of items
            if types[type_name].get("items") != None:
                items_safe = types[type_name]["items"].replace(" ", "_")
                # if items_safe == "base":
                #     items_safe = "object"
                output.write(indent + "type: " + type_safe + "\n")
                output.write(indent + "items: " + items_safe + "\n")

            # otherwise, use the type per normal
            else:
                output.write(indent + "type: " + type_safe + "\n")

            # add the description
            if types[type_name].get("description") != None:
                output.write(indent + "description: " + types[type_name]["description"] + "\n")

            indent = indent[:-2]    # 2

    type_docs = output.getvalue()
    output.close()
    return type_docs


def generate_basic_type_docs(fields, existing_types):
    """Map resource types to their RAML equivalents.
    Expects fields to be a list of modules - each module would be something like pale.fields.
    Expects existing_types to be a list of dict of existing types, which will take precedence
    and prevent a new type with the same name from being added.

    For more on RAML built-in-types, see:
    https://github.com/raml-org/raml-spec/blob/master/versions/raml-10/raml-10.md#built-in-types
    """

    # These types are standard in RAML 1.0
    # They should not be defined in the RAML file that we return
    # We will inherit from them in the types we define
    raml_built_in_types = {
        "any": {
            "parent": None,
        },
        "time-only": {
            "parent": "any",
        },
        "datetime": {
            "parent": "any",
            "pale_children": ["timestamp"],
        },
        "datetime-only": {
            "parent": "any",
        },
        "date-only": {
            "parent": "any",
            "pale_children": ["date"],
        },
        "number": {
            "parent": "any",
        },
        "boolean": {
            "parent": "any",
            "pale_children": ["boolean"]
        },
        "string": {
            "parent": "any",
            "pale_children": ["url", "string", "uri"],
        },
        "null": {
            "parent": "any",
        },
        "file": {
            "parent": "any",
        },
        "array": {
            "parent": "any",
            "pale_children": ["list"],
        },
        "object": {
            "parent": "any",
        },
        "union": {
            "parent": "any",
        },
        "XSD Schema": {
            "parent": "any",
        },
        "JSON Schema": {
            "parent": "any",
        },
        "integer": {
            "parent": "number",
            "pale_children": ["integer"],
        },
    }

    basic_types = {}

    # Find all classes defined in a set of resources and build up an object with
    # the relevant details of the basic types
    for field in fields:

        # if this is a Pale type, it will have a 'value_type' property,
        if hasattr(field, "value_type"):
            type_name = field.value_type.replace(" ", "_")

            # add this type only if it is not in the built-in raml types and we have
            # not added it yet
            if type_name not in raml_built_in_types \
                and type_name not in basic_types \
                and type_name not in existing_types:

                basic_types[type_name] = {}

                # strip newlines and leading whitespaces from doc string, then add as description
                if hasattr(field, "__doc__"):
                    description = field.__doc__
                    modified_description = description_compiler.sub(' ', description, 0)
                    modified_description = colon_compiler.sub(';', modified_description, 0)
                    basic_types[type_name]["description"] = modified_description

                # if this type is listed as the child of a built-in raml type,
                # use the raml type as its parent type
                for raml_type in raml_built_in_types:
                    if "pale_children" in raml_built_in_types[raml_type]:
                        if type_name in raml_built_in_types[raml_type]["pale_children"]:
                            basic_types[type_name]["type"] = raml_type
                            break

                    else:
                        # if this is not the child of a built-in raml type
                        # and if this type is a list composed of other items:
                        if hasattr(field, "is_list") and field.is_list:
                            basic_types[type_name]["type"] = "array"

                            # and the type is defined, use the defined type
                            if hasattr(field, "list_item_type") and field.list_item_type != None:
                                basic_types[type_name]["items"] = field.list_item_type
                            # otherwise, use the base type
                            else:
                                basic_types[type_name]["items"] = "base"


                        # otherwise use the pale parent class as its type
                        else:
                            pale_parent_class = field.__mro__[1]

                            # if we are at the base class, inherit from the RAML "object" type
                            if pale_parent_class.__name__ == "object":
                                basic_types[type_name]["type"] = "object"

                            # otherwise, inherit from the named parent
                            else:
                                basic_types[type_name]["type"] = pale_parent_class.value_type

    ordered_basic_types =  OrderedDict(sorted(basic_types.items(), key=lambda t: t[0]))

    basic_docs = generate_type_docs(ordered_basic_types)

    return (basic_docs, basic_types)


def generate_raml_resource_types(module):
    """Compile a Pale module's resource documentation into RAML format.

    RAML calls Pale resources 'resourceTypes'. This function converts Pale
    resources into the RAML resourceType format.

    The returned string should be appended to the RAML documentation string
    before it is returned.
    """

    from pale import extract_endpoints, extract_resources, is_pale_module
    if not is_pale_module(module):
        raise ValueError(
            """The passed in `module` (%s) is not a pale module. `paledoc`
            only works on modules with a `_module_type` set to equal
            `pale.ImplementationModule`.""")

    module_resource_types = extract_resources(module)
    raml_resource_types_unsorted = {}

    for resource in module_resource_types:
        resource_name = resource.__name__
        raml_resource_types_unsorted[resource_name] = document_resource(resource)
        if hasattr(resource, "_description"):
            modified_description = description_compiler.sub(' ',resource._description, 0)
            modified_description = colon_compiler.sub(';', modified_description, 0)
            raml_resource_types_unsorted[resource_name]["description"] = modified_description

    raml_resource_types_doc = OrderedDict(sorted(raml_resource_types_unsorted.items(), key=lambda t: t[0]))

    output = StringIO()
    indent = "  "  # 2

    # blacklist of resources to ignore
    ignored_resources = []

    for resource_type in raml_resource_types_doc:

        this_resource_type = raml_resource_types_doc[resource_type]

        # add the name, ignoring the blacklist
        if resource_type not in ignored_resources:
            output.write(indent + resource_type + ":\n")

            indent += "  "  # 4

            # add the description
            if this_resource_type.get("description") != None:
                modified_description = description_compiler.sub(' ',this_resource_type["description"], 0)
                modified_description = colon_compiler.sub(';', modified_description, 0)
                output.write(indent + "description: " + modified_description + "\n")

            # if there are no fields, set type directly:
            if len(this_resource_type["fields"]) == 0:
                this_type = "object"
                if this_resource_type.get("_underlying_model") != None:
                    if this_resource_type["_underlying_model"] != object:
                        if hasattr(this_resource_type._underlying_model, "_value_type") \
                        and this_resource_type["_underlying_model"]._value_type not in ignored_resources:
                            this_type = this_resource_type["_underlying_model"]._value_type
                output.write(indent + "type: " + this_type + "\n")

                indent = indent[:-2] # 2

            # if there are fields, use them as the properties, which implies type = object
            else:

                output.write(indent + "properties:\n")
                indent += "  "  # 6

                sorted_fields = OrderedDict(sorted(this_resource_type["fields"].items(), key=lambda t: t[0]))


                # add the field name, a.k.a. RAML type name
                for field in sorted_fields:
                    output.write(indent + field + ":\n")

                    # add the query parameters, a.k.a. RAML properties
                    properties = sorted_fields[field]

                    indent += "  "  # 8

                    # if this type is a list of other types, set it to type 'array' and note the item types
                    # if not, add the type from the Pale type
                    if "_underlying_model" in this_resource_type and this_resource_type["_underlying_model"] == object:
                        output.write(indent + "type: base\n")
                    elif "item_type" in properties:
                        output.write(indent + "type: array\n")
                        output.write(indent + "items: " + properties["item_type"] + "\n")
                    elif "type" in properties:
                        output.write(indent + "type: " + properties["type"].replace(" ", "_") + "\n")

                    # if extended description exists, strip newlines and whitespace and add as description
                    if properties.get("extended_description") != None:
                        description = properties["extended_description"]
                        modified_description = description_compiler.sub(' ', description, 0)
                        modified_description = colon_compiler.sub(';', modified_description, 0)
                        output.write(indent + "description: " + modified_description + "\n")
                    # otherwise, use description
                    elif properties.get("description") != None:
                        modified_description = description_compiler.sub(' ', properties["description"], 0)
                        modified_description = colon_compiler.sub(';', modified_description, 0)
                        output.write(indent + "description: " + modified_description + "\n")

                    if properties.get("default_fields") != None:
                        output.write(indent + "properties:\n")
                        indent += "  " # 10
                        for field_name in sorted(properties["default_fields"]):
                            # @TODO check if every default field is actually a string type
                            output.write(indent + field_name + ": string\n")

                        indent = indent[:-2] # 8

                    indent = indent[:-2] # 6

                indent = indent[:-4] # 2


    raml_resource_types = output.getvalue()
    output.close()
    return raml_resource_types



def generate_raml_tree(flat_resources, version):
    """Generate a dict of OrderedDicts, using the URIs of the Pale endpoints as the structure for the tree.
    Each level of the tree will contain a "path" property and an "endpoint" property.
    The "path" will contain further nested endpoints, sorted alphabetically.
    The "endpoint" will contain the documentation on the endpoint that ends at that level.
    """

    def clean_angle_brackets(string):
        """Remove the angle brackets from a string and return the cleaned string"""
        if string == None:
            result = None
        elif ":" in string:
            path = re.search("(\w+/<\w+)", string).group(0)
            result = re.sub(r'[<]','{', path)
            result += "}"
        else:
            result = re.sub(r'[>]','}', re.sub(r'[<]','{', string))
        return result

    def add_or_find_path(input, tree):
        """Recursively add or find a path to an input dict.
        The tree is a list of directories in nested order.
        Returns a list, containing 1) the innermost node's "endpoint" dict
        and 2) True if it was added as an empty dict, or False if not."""

        # if this is the last branch, return or add and return it
        if len(tree) == 1:
            if input.get(tree[0]) != None \
                and input.get(tree[0]).get("endpoint") != None \
                and len(input.get(tree[0]).get("endpoint")) > 0:
                return [input[tree[0]], False]
            else:
                input[tree[0]] = {}
                input[tree[0]]["path"] = {}
                input[tree[0]]["endpoint"] = {}
                return [input[tree[0]], True]

        # if this is not the last branch, check if it exists and add if necessary
        # then recurse on the next one
        else:
            if input.get(tree[0]) == None:
                input[tree[0]] = {}
                input[tree[0]]["path"] = {}
            return add_or_find_path(input[tree[0]]["path"], tree[+1:])

    def sort_tree_alphabetically(tree):
        """Recursively sort a tree by the keys in each "path" dict.
        Each "path" dict will be converted to an OrderedDict that is sorted alphabetically.
        """

        if tree.get("path") != None and len(tree["path"]) > 0:
            sorted_path = OrderedDict(sorted(tree["path"].items(), key=lambda t: t[0]))
            tree["path"] = sorted_path
            for branch in tree["path"]:
                sort_tree_alphabetically(tree["path"][branch])


    # use a combination of three regex patterns to find all the components of the path
    # these will be used to generate the nested dict that we will convert to RAML

    # pattern #1: matches "path/<id:specialchars>"
    re_dir_nested = "(\w+/[<>\w]+:.*>)"
    # pattern #2: matches "path/<id>""
    re_dir_unique = "(\w+/<[\w\(\)\?\!\.\+]+>)"
    # pattern #3: matches "path" or "<id>" not appearing before "<"
    re_dir_either = "([<>\w\(\)\?\!\.\+]+)(?!<)"
    # combine the patterns
    uri_re_pattern = re_dir_nested + "|" + re_dir_unique + "|" + re_dir_either


    resource_tree = {}
    resource_tree["path"] = {}

    for doc in flat_resources:

        if flat_resources[doc].get("uri") != None:
            this_uri = flat_resources[doc]["uri"]
            uri_matches = re.findall(uri_re_pattern, flat_resources[doc]["uri"])
            uri_tree = []

            # treat the 'uri' string as a nested path, parsing out each directory and adding
            # to the 'uri_tree' list from left to right
            # leftmost element in list is root of path
            for match in uri_matches:
                for directory in match:
                    if directory != "" and directory != version:
                        branch = directory
                        matched_group = re.search('([\w+/]?[<:!\?\+\(\.\*\)>\w]+>)', directory)
                        if matched_group:
                            nested_prefix = clean_angle_brackets(directory)
                            if nested_prefix != None:
                                branch = nested_prefix
                        elif "<" in directory:
                            branch = clean_angle_brackets(directory)
                        uri_tree.append(branch)

            # find the path within the tree
            target = add_or_find_path(resource_tree["path"], uri_tree)
            # add the endpoint to the tree
            target[0]["endpoint"] = flat_resources[doc]

    sort_tree_alphabetically(resource_tree)
    return resource_tree


def generate_raml_resources(module, version):
    """Compile a Pale module's endpoint documentation into RAML format.

    RAML calls Pale endpoints 'resources'. This function converts Pale
    endpoints into RAML resource format.

    The returned string should be appended to the RAML documentation file
    before it is returned.
    """

    from pale import extract_endpoints, extract_resources, is_pale_module
    if not is_pale_module(module):
        raise ValueError(
                """The passed in `module` (%s) is not a pale module. `paledoc`
                only works on modules with a `_module_type` set to equal
                `pale.ImplementationModule`.""")

    raml_resources = extract_endpoints(module)
    raml_resource_doc_flat = { ep._route_name: document_endpoint(ep) for ep in raml_resources }
    raml_resource_doc_tree = generate_raml_tree(raml_resource_doc_flat, version)

    # @TODO generate this dynamically
    pale_argument_type_map = {
        "StringArgument": "string",
        "QueryCursorArgument": "string",
        "KeyArgument": "string",
        "IntegerArgument": "integer",
        "BooleanArgument": "boolean",
        "DateArgument": "date",
        "StringChoiceArgument": "string",
        "QueryKindsArgument": "string",
        "StringChoiceArgument": "string",
        "ListArgument": "array"
    }

    def print_resource_tree(tree, output, indent, level=0):
        """Walk the tree and add the appropriate documentation to the output buffer.
        """

        # check for an endpoint at this level first, and add if it exists
        if tree.get("endpoint") != None:
            indent += "  "
            this_endpoint = tree["endpoint"]

            # add the HTTP method
            if this_endpoint.get("http_method") != None:
                output.write(indent + this_endpoint["http_method"].lower() + ":\n")
                indent += "  "

                # add the description
                if this_endpoint.get("description") != None:
                    modified_description = description_compiler.sub(' ', this_endpoint["description"], 0)
                    output.write(indent + "description: " + modified_description + "\n")

                # add queryParameters per RAML spec
                if this_endpoint.get("arguments") != None and len(this_endpoint["arguments"]) > 0:
                    output.write(indent + "queryParameters:\n")
                    sorted_arguments = OrderedDict(sorted(this_endpoint["arguments"].items(), key=lambda t: t[0]))
                    indent += "  "

                    for argument in sorted_arguments:
                        output.write(indent + argument + ":\n")
                        indent += "  "
                        this_argument = sorted_arguments[argument]

                        for arg_detail in this_argument:
                            # check for special kinds of queryParameters
                            this_arg_detail = this_argument[arg_detail]

                            if this_arg_detail != None:

                                if arg_detail == "default":
                                    output.write(indent + arg_detail + ": " + str(this_arg_detail) + "\n")
                                elif arg_detail == "description":
                                    output.write(indent + "description: " + this_arg_detail + "\n")
                                elif arg_detail == "type":
                                    if pale_argument_type_map.get(this_arg_detail) != None:
                                        if pale_argument_type_map[this_arg_detail] == "array":
                                            # @TODO set the items dynamically
                                            output.write(indent + "type: array\n")
                                            output.write(indent + "items: string\n")
                                        else:
                                            output.write(indent + "type: " + pale_argument_type_map[this_arg_detail].replace(" ", "_") + "\n")
                                    else:
                                        output.write(indent + "type: " + this_arg_detail.replace(" ", "_") + "\n")
                                elif arg_detail == "required":
                                    output.write(indent + "required" + ": " + str(this_arg_detail).lower() + "\n")
                                elif arg_detail == "min_length":
                                    output.write(indent + "minLength: " + str(this_arg_detail) + "\n")
                                elif arg_detail == "max_length":
                                    output.write(indent + "maxLength: " + str(this_arg_detail) + "\n")
                                elif arg_detail == "min_value":
                                    output.write(indent + "minimum: " + str(this_arg_detail) + "\n")
                                elif arg_detail == "max_value":
                                    output.write(indent + "maximum: " + str(this_arg_detail) + "\n")

                        indent = indent[:-2]    # reset indent after arg_detail

                    indent = indent[:-2]    # reset indent after argument

                # add the responses
                if this_endpoint.get("returns") != None and len(this_endpoint["returns"]) > 0:
                    output.write(indent + "responses:\n")
                    this_response = this_endpoint["returns"]
                    indent += "  "

                    # @TODO refactor the endpoints so that they use a variable called _success
                    # to determine the HTTP code for a successful response
                    # (see changes made to history.py)

                    if this_response.get("success") != None:
                        output.write(indent + str(this_response["success"]) + ":\n")
                    else:
                        output.write(indent + "200:\n")
                    indent += "  "
                    output.write(indent + "body:\n")
                    indent += "  "

                    for res_detail in this_response:
                        if res_detail != "success":
                            if res_detail == "resource_type":
                                output.write(indent + "type: " + this_endpoint["returns"][res_detail].replace(" ", "_") + "\n")
                            elif res_detail == "description":
                                modified_description = string_format_compiler.sub("", this_endpoint["returns"][res_detail], 0).replace("  ", " ")
                                output.write(indent + "description: " + modified_description + "\n")

                    indent = indent [:-6]   # resent indent after responses

                indent = indent [:-2]   # reset indent after endpoint

        # check for further branches and recurse on them
        if tree.get("path") != None and len(tree["path"]) > 0:
            # only increase the indent if we are not on root level
            if level > 0:
                # set the base indentation per the level we are at in the tree
                indent = level * "  "
            for branch in tree["path"]:
                output.write(indent + "/" + branch + ":\n")
                print_resource_tree(tree["path"][branch], output, indent, level=level+1)


    output = StringIO()
    indent = ""
    print_resource_tree(raml_resource_doc_tree, output, indent)
    raml_resources = output.getvalue()
    output.close()
    return raml_resources



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
    ep_doc = { ep._route_name: document_endpoint(ep) for ep \
            in module_endpoints }

    module_resources = extract_resources(module)
    res_doc = { r._value_type: document_resource(r) for r \
            in module_resources }

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
        'returns': format_endpoint_returns_doc(endpoint),
    }
    if hasattr(endpoint, "_success"):
        docs["success"] = endpoint._success
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
        'default_fields': None,
    }
    if resource._default_fields:
        res_doc['default_fields'] = list(resource._default_fields)
    return res_doc
