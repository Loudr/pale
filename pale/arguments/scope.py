from pale.arguments.string import StringListArgument

class ScopeArgument(StringListArgument):
    """A field for OAuth 2.0 Scope strings.

    This is basically just a space-separated string list"""

    def __init__(self, *args, **kwargs):
        kwargs['separator'] = ' '
        super(ScopeArgument, self).__init__(*args, **kwargs)
