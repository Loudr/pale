class PaleBaseResponse(object):
    @property
    def response(self):
        http_status = getattr(self, 'http_status_code', 418)
        response_body = getattr(self, 'response_body', "i am a teapot")
        headers = getattr(self, 'headers', {})
        return (response_body, http_status, headers)

class PaleRaisedResponse(PaleBaseResponse, Exception):
    pass


class RedirectFound(PaleRaisedResponse):
    http_status_code = 302
    response_body = ""

    def __init__(self, redirect_url):
        self.redirect_url = redirect_url

    @property
    def headers(self):
        return {
            'Location': self.redirect_url
        }

