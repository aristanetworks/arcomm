# -*- coding: utf-8 -*-

"""
"""

import importlib
import re
import time
from urlparse import urlparse
from arcomm.util import session_defaults, to_list, parse_uri, merge_dicts
from arcomm.command import Command
from arcomm.response import ResponseStore, Response
from arcomm.protocols.ssh import Ssh
from arcomm.credentials import BasicCreds
from arcomm.exceptions import ExecuteFailed

DEFAULTS = session_defaults()
DEFAULT_TIMEOUT = DEFAULTS.get('timeout', 30)
DEFAULT_PROTOCOL = DEFAULTS.get('protocol', 'eapi+http')
DEFAULT_CREDS = DEFAULTS.get('creds')
DEFAULT_HOST = DEFAULTS.get('host', 'localhost')

def _to_commands(commands):
    """Converts a command or list of commands to a list of Command objects"""
    commands = to_list(commands)
    _loc = []
    for _cmd in commands:
        if not isinstance(_cmd, Command):
            if re.search("^(!|#)", _cmd) or re.search("^\s*$", _cmd):
                continue
            _cmd = Command(_cmd.strip())
        _loc.append(_cmd)
    return _loc

def _load_protocol_adapter(name):
    """Load protocol module from name"""

    if __name__ == '__main__':
        raise ValueError('Failed load protocol adapters when this module ' +
                         'is run directly')

    package, _ = __name__.split('.', 1)
    path = '.'.join((package, 'protocols', name))
    module = importlib.import_module(path)
    class_ = re.sub(r'_', '', name.title())

    # Finally, we retrieve the Class
    return getattr(module, class_)

class Session(object):
    """
    Base Session
    """

    def __init__(self):

        #
        self.authorized = False

        # connection object returned by the protocol adapter
        self.conn = None

        # # Credentials tuple or object to pass to adapter
        # self.creds = DEFAULT_CREDS

        # host to connect to
        self.hostname = DEFAULT_HOST

        # Protocol adapter to load
        self.protocol = DEFAULT_PROTOCOL

        # timeout in seconds
        self.options = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def connect(self, uri, **kwargs):
        """Connect to the remote host"""

        options = merge_dicts(parse_uri(uri), kwargs)

        self.hostname = options.get('hostname') or self.hostname
        protocol = options.get('protocol') or self.protocol

        if '+' in protocol:
            protocol, transport = self.protocol.split('+', 1)
            options['transport'] = transport
        else:
            options['transport'] = options.get('transport')
        self.protocol = protocol

        options['creds'] = options.get('creds') or DEFAULT_CREDS
        port = options.get('port')

        if port:
            options['port'] = port

        options['timeout'] = options.get('timeout') or DEFAULT_TIMEOUT

        self.options = options

        self.conn = _load_protocol_adapter(protocol)()
        self.conn.connect(self.hostname, **self.options)

    def authorize(self, password='', username=None):
        self.conn.authorize(password, username)
        self.authorized=True

    enable = authorize

    def execute(self, commands, **kwargs):
        """send commands"""

        store = ResponseStore(host=self.hostname)

        commands = _to_commands(commands)

        try:
            responses = self.conn.send(commands, **kwargs)

            for item in zip(commands, responses):

                if not hasattr(item, '__iter__') or len(item) > 2:
                    raise TypeError('response must be an iterable containing ' +
                                    'two items: (output, errors)')

                command, response = item
                store.append(Response(command.cmd, response))

            store.status = 'ok'

        except ExecuteFailed as exc:
            store.status = 'failed'

        return store

    def clone(self, uri=None, **kwargs):
        cloned = self.__class__()
        if not uri:
            uri = self.hostname
        kwargs = merge_dicts(self.options, parse_uri(uri), kwargs)
        cloned.connect(uri, **kwargs)
        return cloned

    def close(self):
        if hasattr(self.conn, 'close'):
            self.conn.close()

def session():
    return Session()
