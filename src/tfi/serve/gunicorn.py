from tfi.http.flask import make_app, make_deferred_app
from gunicorn.arbiter import Arbiter
from gunicorn.config import Config
from gunicorn import util

class _GunicornApplication(object):
    def __init__(self, application, options={}):
        cfg = Config(None, prog=None)
        for k, v in options.items():
            if k.lower() in cfg.settings and v is not None:
                cfg.set(k.lower(), v)
        self.cfg = cfg
        self.application = application

    def wsgi(self):
        return self.application

def run_app(app, host, port):
    options = {
        'bind': '%s:%d' % (host, port),
    }
    Arbiter(_GunicornApplication(app, options)).run()

def run(model, host, port):
    run_app(make_app(model), host, port)

def run_deferred(host, port):
    run_app(make_deferred_app(), host, port)