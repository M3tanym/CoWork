"""
web_server.py
Runs HTTP and WebSocket server
"""

# Project imports
from noapi import __version__ as version

# Python imports
from threading import Thread
from queue import Empty

# Third-party imports
from bottle import Bottle, static_file, request, response
from bottle_websocket import websocket
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from gevent import Timeout


class WebServer(Thread):
    def __init__(self, queue, reply, port, content):
        super().__init__()
        self._queue = queue
        self._reply = reply
        self._port = port
        self._content = content
        self._server = None

    def run(self):
        # self._reply(f'Running server on port {self._port}')
        app = Bottle()
        self._server = WSGIServer(('0.0.0.0', self._port), app, handler_class=WebSocketHandler)

        @app.get('/')
        def index():
            return static_file('index.html', root=self._content)

        @app.get('/<filepath:path>')
        def send_resource(filepath):
            return static_file(filepath, root=self._content)

        @app.get('/ws', apply=[websocket])
        def web_socket(ws):
            # self._reply(f"{request.environ['REMOTE_ADDR']} - - WebSocket Connected")
            # clear messages when reconnecting
            self._queue.queue.clear()
            while not ws.closed:
                try:
                    with Timeout(0.1, False):
                        msg = ws.receive()
                        if msg is not None:
                            self._reply(msg)

                except WebSocketError:
                    break
                try:
                    msg = self._queue.get_nowait()
                    # print(f'SENDING {msg}')
                    ws.send(msg)
                except Empty:
                    pass
            # self._reply(f"{request.environ['REMOTE_ADDR']} - - WebSocket Disconnected")

        self._server.serve_forever()

    def stop(self):
        self._server.stop()
