# -*- coding: utf-8 -*-

"""
"""

import importlib
import re
from urlparse import urlparse
from arcomm.util import session_defaults, to_list, parse_uri
from arcomm.command import Command
from arcomm.response import ResponseStore, Response
from arcomm.protocols.ssh import Ssh
from arcomm.credentials import BasicCreds

DEFAULTS = session_defaults()
DEFAULT_TIMEOUT = DEFAULTS.get('timeout', 30)
DEFAULT_PROTOCOL = DEFAULTS.get('protocol', 'eapi+http')
DEFAULT_CREDS = DEFAULTS.get('creds')
DEFAULT_HOST = DEFAULTS.get('host', 'localhost')

def to_list_of_commands(commands):
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

        # timeout in seconds
        self.timeout = DEFAULT_TIMEOUT

        # Protocol adapter to load
        self.protocol = DEFAULT_PROTOCOL

        # Credentials tuple or object to pass to adapter
        self.creds = DEFAULT_CREDS

        # host to connect to
        self.host = DEFAULT_HOST

        # connection object returned by the protocol adapter
        self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _validate_responses(self, commands, responses):
        pass

    def connect(self, uri, options={}):
        """Connect to the remote host"""

        parts = parse_uri(uri)

        creds = options.get('creds', parts.get('creds', self.creds))

        hostname = parts['hostname']
        protocol = parts['protocol']

        if parts['port']:
            options['port'] = parts['port']

        options['timeout'] = options.get('timeout', self.timeout)



        # clean up names like: eapi+https
        if '+' in protocol:
            protocol, transport = parts.scheme.split('+', 1)
            options['transport'] = transport

        self.conn = _load_protocol_adapter(protocol)()
        self.conn.connect(hostname, creds, options)

    def authorize(self, password='', username=None):
        self.conn.authorize(password, username)

    enable = authorize

    def send(self, commands, options={}):
        """send commands"""

        store = ResponseStore()

        commands = to_list_of_commands(commands)

        responses = self.conn.send(commands, options)

        for item in zip(commands, responses):

            if not hasattr(item, '__iter__') or len(item) > 2:
                raise TypeError('response must be an iterable containing two ' +
                                'items: (output, errors)')

            command, outerr = item
            store.append(Response(command, outerr[0], outerr[1]))

        return store

    execute = send

    def close(self):
        if hasattr(self.conn, 'close'):
            self.conn.close()
