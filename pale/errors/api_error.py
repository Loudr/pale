from .base import BasePaleError

class APIError(BasePaleError):
    @classmethod
    def Forbidden(cls, message="You don't have permission to do that."):
        err = cls(message)
        err.http_status_code = 403
        return err

    @classmethod
    def NotFound(cls, message):
        err = cls(message)
        err.http_status_code = 404
        return err

    @classmethod
    def UnprocessableEntity(cls, message):
        err = cls(message)
        err.http_status_code = 422
        return err

