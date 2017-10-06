class PaleBaseResponse(object):
    def __init__(self, *args):
        super(PaleBaseResponse, self).__init__(*args)
        if args:
            self.message = args[0]
        else:
            self.message = "i am a teapot"

    @property
    def response(self):
        http_status = getattr(self, 'http_status_code', 418)
        response_body = getattr(self, 'response_body', "i am a teapot")
        headers = getattr(self, 'headers', None)
        return (response_body, http_status, headers)

class PaleRaisedResponse(PaleBaseResponse, Exception):
    pass


class RedirectFound(PaleRaisedResponse):
    http_status_code = 302
    response_body = ""

    def __init__(self, redirect_url):
        self.redirect_url = redirect_url
        super(RedirectFound, self).__init__("Redirect to `%s`" % redirect_url)

    @property
    def headers(self):
        return [('Location', self.redirect_url)]

