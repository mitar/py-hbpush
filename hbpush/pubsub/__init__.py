from tornado.web import RequestHandler, HTTPError
from hbpush.channel import Channel
from hbpush.message import Message


class PubSubHandler(RequestHandler):
    exception_mapping = {
        Channel.DoesNotExist: 404,
        Channel.Duplicate: 409,
        Channel.Gone: 410,
        Channel.NotModified: 304,
        Message.DoesNotExist: 404,
    }

    def __init__(self, *args, **kwargs):
        self.registry = kwargs.pop('registry', None)
        self.servername = kwargs.pop('servername', None)
        self.allow_origin = kwargs.pop('allow_origin', '*')
        self.allow_credentials = kwargs.pop('allow_credentials', False)
        if (self.allow_origin == '*' and self.allow_credentials):
            raise AttributeError("allow_origin cannot be '*' with allow_credentials set to true")
        super(PubSubHandler, self).__init__(*args, **kwargs)

    def add_vary_header(self):
        self.set_header('Vary', 'If-Modified-Since, If-None-Match')

    def add_accesscontrol_headers(self):
        self.set_header('Access-Control-Allow-Origin', self.allow_origin)
        self.set_header('Access-Control-Allow-Headers', 'If-Modified-Since, If-None-Match, X-Cookie')
        self.set_header('Access-Control-Expose-Headers', 'Last-Modified, Etag, Cache-Control')
        self.set_header('Access-Control-Allow-Credentials', 'true' if self.allow_credentials else 'false')
        self.set_header('Access-Control-Max-Age', '864000')

    def set_default_headers(self):
        if self.servername:
            self.set_header('Server', self.servername)

    def _handle_request_exception(self, e):
        if e.__class__ in self.exception_mapping:
            e = HTTPError(self.exception_mapping[e.__class__], str(e))

        super(PubSubHandler, self)._handle_request_exception(e)

    errback = _handle_request_exception

    def simple_finish(self, *args, **kwargs):
        # ignore everything, and just finish the request
        self.finish()

