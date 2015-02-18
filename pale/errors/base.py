from pale.response import PaleBaseResponse

class BasePaleError(PaleBaseResponse, Exception):
    http_status_code = 500

    @property
    def response_body(self):
        return '{"error": "%s"}' % (self.message, )
