from .base import BasePaleError

class ArgumentError(BasePaleError):
    def __init__(self, arg_name, message):
        error_msg = ("Invalid argument: `%s`.  %s"
                % (arg_name, message))
        self.arg_name = arg_name
        super(ArgumentError, self).__init__(error_msg)


class AuthenticationError(BasePaleError):
    pass
