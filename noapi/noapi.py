"""
NoAPI is a micro-framework, maybe?
Homepage and documentation: NOAPI
Copyright (c) 2022 Ben Gillett
License: MIT (see LICENSE for details)
"""

# Python imports
import functools
from time import sleep
from queue import Queue
import json
from json import JSONDecodeError
from threading import Thread
import uuid

# Project imports
from noapi.web_server import WebServer
from noapi.callbox import Callbox


class NoAPIException(Exception):
    pass


class NoAPI(object):
    def __init__(self):
        super().__init__()

        self.q = Queue()
        self._js_calls = {}
        self._py_calls = {}
        self._webserver = None

        self._running = True
        self.on_info = lambda msg: None

    def _run_server(self, port, content):
        def rx(msg):
            self._process_msg(msg)
        webserver = WebServer(self.q, rx, port, content)
        webserver.daemon = True
        webserver.start()
        self._webserver = webserver

    def _process_msg(self, raw_msg):
        try:
            json_msg = json.loads(raw_msg)
            self._eval_msg(json_msg)
        except JSONDecodeError:
            raise NoAPIException(f'Message caused error: {raw_msg}')

    def _eval_msg(self, json_msg):
        t = json_msg['type']
        del json_msg['type']
        actions = {
            'info': self._handle_info,
            'call': self._handle_call,
            'return': self._handle_return
        }
        actions[t](json_msg)

    def _handle_info(self, data):
        msg = data['msg']
        self.on_info(msg)

    def _handle_call(self, data):
        fn = data['fn']
        f = self._py_calls[fn]
        fid = data['fid']
        args = []
        kwargs = {}
        try:
            a = data['args']
            if type(a) is list:
                args = a
            k = data['kwargs']
            if type(k) is dict:
                kwargs = k
        except KeyError:
            pass

        k = {'f': f, 'fid': fid, 'args': args, 'kwargs': kwargs}
        t = Thread(target=self._th_wrapper, kwargs=k)
        t.daemon = True
        t.start()

    def _handle_return(self, data):
        fid = data['fid']
        ret = data['ret'] if 'ret' in data else None
        cb = self._js_calls[fid]
        cb.on_return(ret)

    def _th_wrapper(self, f, fid, args, kwargs):
        ret = f(*args, **kwargs)
        self.raw({'type': 'return', 'fid': fid, 'ret': ret})

    def run_forever(self):
        try:
            while self._running:
                sleep(1)
        except KeyboardInterrupt:
            pass

    def run(self, port, content):
        self._run_server(port, content)
        return self

    def raw(self, json_msg):
        self.q.put(json.dumps(json_msg))

    def info(self, msg):
        self.raw({'type': 'info', 'data': msg})

    def call(self, fn, args=None):
        fid = str(uuid.uuid4())
        cb = Callbox(fid)
        self._js_calls[fid] = cb
        self.raw({'type': 'call', 'fn': fn, 'fid': fid, 'args': args})
        return cb

    def register(self, name):
        def decorator(function):
            self._py_calls[name] = function
            return function

        return decorator


class AppStack(list):
    """ A stack-like list. Calling it returns the head of the stack. """

    def __call__(self):
        """ Return the current default application. """
        return self[-1]

    def push(self, value=None):
        """ Add a new instance to the stack """
        if not isinstance(value, NoAPI):
            value = NoAPI()
        self.append(value)
        return value


app = default_app = AppStack()
app.push()


def make_default_app_wrapper(name):
    @functools.wraps(getattr(NoAPI, name))
    def wrapper(*a, **ka):
        return getattr(app(), name)(*a, **ka)
    return wrapper


run = make_default_app_wrapper('run')
register = make_default_app_wrapper('register')
call = make_default_app_wrapper('call')
info = make_default_app_wrapper('info')
