from functools import wraps

authenticate_context = None
create_context = None


def context_creator(f):
    """A wrapper to allow developers to set a context creator that's appropriate
    for their particular API.
    """
    global create_context
    create_context = f
    return f


def authenticator(f):
    """A wrapper to allow developers to set a context creator that's appropriate
    for their particular API.
    """
    global authenticate_context
    authenticate_context = f
    return f
