# coding: utf-8
from wsgiref.simple_server import WSGIRequestHandler, SimpleHandler


class ServerHandler(SimpleHandler):
    os_environ = {}

    def handle_error(self):
        pass

    def setup_environ(self):
        env = self.environ = self.os_environ.copy()
        self.add_cgi_vars()

        env['wsgi.output'] = self.stdout
        env['wsgi.input'] = self.get_stdin()
        env['wsgi.errors'] = self.get_stderr()
        env['wsgi.version'] = self.wsgi_version
        env['wsgi.run_once'] = self.wsgi_run_once
        env['wsgi.url_scheme'] = self.get_scheme()
        env['wsgi.multithread'] = self.wsgi_multithread
        env['wsgi.multiprocess'] = self.wsgi_multiprocess

        if self.wsgi_file_wrapper is not None:
            env['wsgi.file_wrapper'] = self.wsgi_file_wrapper

        if self.origin_server and self.server_software:
            env.setdefault('SERVER_SOFTWARE', self.server_software)

    def close(self):
        SimpleHandler.close(self)


class WithoutLogHandler(WSGIRequestHandler):

    def log_error(self, *args, **kwargs) -> None:
        pass

    def log_message(self, *args, **kwargs) -> None:
        pass

    def log_request(self, *args, **kwargs) -> None:
        pass

    def handle(self):
        self.raw_requestline = self.rfile.readline(65537)
        if len(self.raw_requestline) > 65536:
            self.requestline = ''
            self.request_version = ''
            self.command = ''
            self.send_error(414)
            return

        if not self.parse_request():
            return

        handler = ServerHandler(
            self.rfile, self.wfile, self.get_stderr(), self.get_environ()
        )
        handler.request_handler = self
        handler.run(self.server.get_app())
