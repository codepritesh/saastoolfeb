# coding=utf-8
import os, sys
import json
from functools import wraps
from threading import Thread
from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       connectWS
from twisted.internet import reactor, ssl
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.error import ReactorAlreadyRunning

this_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(this_path)
from common import datetime_now

def json_decoder(payload):
    return json.loads(payload.decode('utf8'))

def on_message_handler(decoder=json_decoder):
    def decorator(func):
        @wraps(func)
        def func_wrapper(obj, payload, isBinary=False):
            try:
                msg = decoder(payload)
            except ValueError:
                pass
            else:
                func(obj, msg)
        return func_wrapper
    return decorator

class CommonClientProtocol(WebSocketClientProtocol):
    def __init__(self, factory, payload=None, credential=None):
        super().__init__()
        self.factory = factory
        self.payload = payload
        self.credential = credential

    def onOpen(self):
        self.factory.protocol_instance = self

    def onConnect(self, response):
        if self.credential:
            self.sendMessage(self.credential, isBinary=False)
        if self.payload:
            self.sendMessage(self.payload, isBinary=False)
        # reset the delay after reconnecting
        self.factory.resetDelay()

    def onMessage(self, payload, isBinary):
        # This will call @on_message_handler
        self.factory.callback(payload, isBinary)

class CommonClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    # Overwrite attributes of ReconnectingClientFactory
    # Set initial delay to a short time
    initialDelay = 0.1
    maxDelay = 10
    maxRetries = 60

    # Set factory protocol
    protocol = CommonClientProtocol

    ERROR_TEMPLATE = {
        'e': '',
        'm': 'Max reconnect retries reached',
        'r': None,
        'p': None,
        't': ''
    }

    def __init__(self, *args, payload=None, credential=None, **kwargs):
        WebSocketClientFactory.__init__(self, *args, **kwargs)
        self.protocol_instance = None
        self.base_client = None
        self.payload = payload
        self.credential = credential

    def __error(self, what, reason):
        _error = self.ERROR_TEMPLATE.copy()
        _error['e'] = what
        _error['r'] = reason
        _error['p'] = self.url
        _error['t'] = datetime_now()
        print(_error)

    def clientConnectionFailed(self, connector, reason):
        self.retry(connector)
        if self.retries > self.maxRetries:
            self.__error('clientConnectionFailed', reason)

    def clientConnectionLost(self, connector, reason):
        self.retry(connector)
        if self.retries > self.maxRetries:
            self.__error('clientConnectionLost', reason)

    def buildProtocol(self, addr):
        return CommonClientProtocol(self, payload=self.payload, credential=self.credential)


class CommonSocketManager(Thread):
    STREAM_URL = ''

    def __init__(self):  # client
        """Initialize the CommonSocketManager"""
        Thread.__init__(self)
        self.factories = {}
        self._conns = {}

    def __add_connection(self, conn_id, url):
        """
        Convenience function to connect and store the connector.
        """
        if not url.startswith("wss://"):
            raise ValueError('expected "wss://" prefix')
        hostname = url[6:]
        hostname = hostname.split(':')[0] # strip ':' and afterward if any
        hostname = hostname.split('/')[0] # strip '/' and afterward if any
        factory = self.factories[conn_id]
        #context_factory = ssl.ClientContextFactory()
        options = ssl.optionsForClientTLS(hostname=hostname) # for TLS SNI
        self._conns[conn_id] = connectWS(factory, options)

    def _start_socket(self, conn_id, payload, credential, callback):
        if conn_id in self._conns:
            return False

        factory_url = self.STREAM_URL
        factory = CommonClientFactory(factory_url, payload=payload, credential=credential)
        factory.base_client = self
        factory.protocol = CommonClientProtocol
        factory.callback = callback
        factory.reconnect = True
        factory.isSecure = True
        self.factories[conn_id] = factory
        reactor.callFromThread(self.__add_connection, conn_id, factory_url)
        return conn_id

    def _stop_socket(self, conn_id):
        if conn_id not in self._conns:
            return

        # disable reconnecting if we are closing
        self._conns[conn_id].factory = WebSocketClientFactory(self.factories[conn_id].url)
        self._conns[conn_id].disconnect()
        del self._conns[conn_id]
        del self.factories[conn_id]

    def run(self):
        try:
            reactor.run(installSignalHandlers=False)
        except ReactorAlreadyRunning:
            # Ignore error about reactor already running
            pass

    def close(self):
        """
        Close all connections
        """
        conns = set(self._conns.keys())
        for key in conns:
            self._stop_socket(key)
        self._conns = {}

    def stop(self):
        """Tries to close all connections and finally stops the reactor.
        Properly stops the program."""
        try:
            self.close()
        finally:
            pass
            #FIXME Dangerous!!
            #reactor.stop()
