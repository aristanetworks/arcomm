# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from getpass import getpass
import importlib
import re
import time
from arcomm import env
from arcomm.util import to_list, parse_endpoint, deepmerge
from arcomm.command import commands_from_list
from arcomm.response import ResponseStore, Response
from arcomm.credentials import BasicCreds
from arcomm.exceptions import ExecuteFailed

#from urlparse import urlparse
from future.standard_library import install_aliases
install_aliases()
from urllib.parse import urlparse

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

    def __init__(self, endpoint, **kwargs):
        # connection object returned by the protocol adapter
        self._conn = None
        # true if session is authorized (enabled)
        self.authorized = False

        self.params = kwargs

        endpoint = parse_endpoint(endpoint)

        self.hostname = endpoint['hostname']

        # handle creds
        if endpoint['username']:
            password = endpoint['password']
            if password is None:
                password = ""
            creds = (endpoint['username'], password)
        else:
            creds = (self.params.get('creds', None)
                or (env.ARCOMM_DEFAULT_USERNAME, env.ARCOMM_DEFAULT_PASSWORD))

        if self.params.get('askpass'):
            password = getpass("{}@{}'s password:".format(creds[0], self.hostname))
            creds = (creds[0], password)

        self.params['creds'] = self._handle_creds(creds)

        # handle protocol and transport
        protocol = (endpoint['protocol'] or self.params.get('protocol')
                    or env.ARCOMM_DEFAULT_PROTOCOL)

        if '+' in protocol:
            protocol, transport = protocol.split('+', 1)
            self.params['transport'] = transport

        self.params['protocol'] = protocol
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
        self._conn.connect(self.hostname, **self.params)

    def authorize(self, password='', username=None):
        self._conn.authorize(password, username)
        self.authorized = (password, username)

    enable = authorize

    def clone(self, hostname=None, **kwargs):
        if not hostname:
            hostname = self.hostname

        params = deepmerge(self.params, kwargs)

        cloned = Session(hostname, **params)
        cloned.connect()
        return cloned

    def close(self):
        if hasattr(self._conn, 'close'):
            self._conn.close()

        self._conn = None

    def send(self, commands, **kwargs):
        """send commands"""

        store = ResponseStore(host=self.hostname)

        if 'callback' in kwargs:
            store.subscribe(kwargs['callback'])

        commands = commands_from_list(commands)

        try:
            responses = self._conn.send(commands, **kwargs)

            for item in zip(commands, responses):
                command, response = item

                store.append((command.cmd, response))

        except ExecuteFailed as exc:
            store.append(Response(exc.command, str(exc), errored=True))

        return store

    execute = send

class UntilMixin(object):

    def execute_until(self, commands, condition, **kwargs):
        """Runs a command until a condition has been met or the timeout
        (in seconds) is exceeded. If 'exclude' is set this function will return
        only if the string is _not_ present"""

        timeout = kwargs.pop('timeout', None) or env.ARCOMM_DEFAULT_TIMEOUT
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
