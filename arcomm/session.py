# -*- coding: utf-8 -*-

"""
"""

import importlib
import re
import time
from urlparse import urlparse
from arcomm.util import session_defaults, to_list, parse_endpoint, deepmerge
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

    package = None
    if __name__ == '__main__':
        package = 'arcomm'
    else:
        package, _ = __name__.split('.', 1)

    path = '.'.join((package, 'protocols', name))
    module = importlib.import_module(path)
    class_ = re.sub(r'_', '', name.title())

    # Finally, we retrieve the Class
    return getattr(module, class_)

class BaseSession(object):
    """
    Base Session
    """

    def __init__(self, endpoint, creds=None, protocol=None, **kwargs):

        # connection object returned by the protocol adapter
        self._conn = None

        # true if session is authorized (enabled)
        self.authorized = False

        #
        self.options = kwargs

        endpoint = parse_endpoint(endpoint)

        #
        self.hostname = endpoint['hostname']

        # Credentials tuple or object to pass to adapter
        if creds:
            creds = self._handle_creds(creds)
        else:
            creds = endpoint.get('creds') or DEFAULT_CREDS

        #
        self.creds = creds

        if not protocol:
            protocol = endpoint.get('protocol') or DEFAULT_PROTOCOL

        # setup protocol and transport
        if '+' in protocol:
            protocol, transport = protocol.split('+', 1)
            self.options['transport'] = transport

        self.protocol = protocol

        self._protocol_adapter = _load_protocol_adapter(protocol)

    def __enter__(self):
        """
        """
        self.connect()
        return self

    def __exit__(self, *args):
        """
        """

        self.close()

    def __repr__(self):
        return str(self.__dict__)

    def _handle_creds(self, creds):
        """
        """
        if isinstance(creds, (tuple, list)):
            creds = BasicCreds(*creds)
        return creds

    def connect(self): #, uri, **kwargs):
        """Connect to the remote host"""

        self._conn = self._protocol_adapter()
        self._conn.connect(self.hostname, self.creds, **self.options)

    def authorize(self, password='', username=None):
        self._conn.authorize(password, username)
        self.authorized = (password, username)

    enable = authorize

    def send(self, commands, **kwargs):
        """send commands"""

        store = ResponseStore(host=self.hostname)

        commands = _to_commands(commands)

        try:
            responses = self._conn.send(commands, **kwargs)

            for item in zip(commands, responses):
                command, response = item
                store.append(Response(command.cmd, response))

            store.status = 'ok'

        except ExecuteFailed as exc:
            store.append(Response(exc.command, exc.message))
            store.status = 'failed'

        return store

    execute = send

    # endpoint, creds=None, protocol=None, options={}
    def clone(self, hostname=None, creds=None, protocol=None, **kwargs):
        """
        """

        if not hostname:
            hostname = self.hostname

        if creds:
            creds = self._handle_creds(creds)
        else:
            creds = self.creds

        if not protocol:
            protocol = self.protocol

        options = deepmerge(kwargs, self.options)

        cloned = Session(hostname, creds, protocol, **options)
        cloned.connect()
        return cloned

    def close(self):
        if hasattr(self._conn, 'close'):
            self._conn.close()

        self._conn = None

class UntilMixin(object):

    def execute_until(self, commands, condition, **kwargs):
        """Runs a command until a condition has been met or the timeout
        (in seconds) is exceeded. If 'exclude' is set this function will return
        only if the string is _not_ present"""

        timeout = kwargs.pop('timeout', None) or 30
        sleep = kwargs.pop('sleep', None) or 1
        exclude = kwargs.pop('exclude', False)

        start_time = time.time()
        check_time = start_time
        response = None

        while (check_time - timeout) < start_time:
            response = self.execute(commands, **kwargs)

            match = re.search(re.compile(condition), str(response))
            if exclude:
                if not match:
                    return response
            elif match:
                return response
            time.sleep(sleep)
            check_time = time.time()

        raise ValueError("condition did not match withing timeout period")

    def execute_while(self, commands, condition, **kwargs):
        self.execute_until(commands, condition, exclude=True, **kwargs)

class Session(UntilMixin, BaseSession):
    pass

def session(*args, **kwargs):
    return Session(*args, **kwargs)
