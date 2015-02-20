import re
import sys


# this guy matches a single newline, but omits chunks of newlines strewn
# together, so that a string like "hi i am\nsome documentation\n\nhello"
# can be substituted to read "hi i am some documentation\n\nhello"
newline_substitution_regex = re.compile(r"(?<!\n)\n(?!\n)")


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
