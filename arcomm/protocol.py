# -*- coding: utf-8 -*-
"""Base module for protocol adapters"""
import re
from arcomm.command import Command
from arcomm.util import to_list
from arcomm.exceptions import ProtocolException, AuthorizationFailed, \
                              ConnectFailed, ExecuteFailed
from arcomm.response import Response, ResponseStore
from arcomm.env import ARCOMM_DEFAULT_PROTOCOL, ARCOMM_DEFAULT_TIMEOUT
# DEFAULT_PROTOCOL = ["eapi", "ssh"]
# DEFAULT_TIMEOUT = 30

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

class Protocol(object):
    """Base class for protocol adapters"""
    def __init__(self, host, creds, timeout=None, **kwargs):
        self._host = host
        self._creds = creds
        self._timeout = timeout or 300
        self._connected = False
        self._connection = None
        self._authorized = False
        self._keywords = kwargs
        self._responses = ResponseStore(host=self._host)
        self._on_initialize(**kwargs)

    def __enter__(self):
        self.connect()

    def __exit__(self, type, value, tb):
        self.close()

    @property
    def authorized(self):
        """Return True if protocol has been authorized"""
        return self._authorized

    @property
    def connected(self):
        """Return True if a conenctions has been made"""
        return self._connected

    @property
    def connection(self):
        """Hold the connection for the lower level protocols"""
        return self._connection

    @property
    def creds(self):
        """Hold the creds object"""
        return self._creds

    @property
    def host(self):
        """Return hostname or IP address"""
        return self._host

    @property
    def protocol(self):
        """Returns the lowered class named"""
        return self.__class__.__name__.lower()

    @property
    def responses(self):
        """Return the responses from all commands sent"""
        return self._responses

    @property
    def timeout(self):
        """Return the timeout value (in seconds)"""
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        """Sets the timeout value (in seconds)"""
        if not isinstance(value, int):
            raise ValueError("Timeout value must be an integer.")
        self._timeout = value

    def _authorize(self, secret):
        """Implemented by a protocol to handle authorization. i.e. su, sudo or
        enable"""
        pass

    def _close(self):
        """Overridden by sub-class for closing connections"""
        pass

    def _connect(self, host, creds):
        """Makes the connection to the remote host. Implemented by lower
        layer"""
        raise NotImplementedError("Must be implemented by protocol")

    def _on_connect(self):
        """Implmented by the protocol, called after connect"""
        pass

    def _on_initialize(self, **kwargs):
        """Implmented by the protocol, called at end of __init__"""
        pass

    def _send(self, command, **kwargs):
        """Called for each command sent to 'execute'"""

    def _sendall(self, commands, **kwargs):
        """Called for each command sent to 'execute'"""

    def authorize(self, secret=None):
        """Authorize the connection for elevated commands and configuration
        changes"""

        try:
            self._authorize(secret)
        except ProtocolException as exc:
            _message = "Authorization failed with error: {}".format(exc.message)
            raise AuthorizationFailed(exc.message)

        self._authorized = True

    def close(self):
        """Disconnects from the host and closes the connection"""

        self._close()
        self._connected = False

    def connect(self):
        """Connects to a host an sets 'connected' to True"""

        self._connection = self._connect(self.host, self.creds)

        # auto-authorize if password is not None
        if self.creds.authorize_password is not None:
            self.authorize(self.creds.authorize_password)

        self._on_connect()
        self._connected = True

    reconnect = connect

    def execute(self, commands, **kwargs):
        """Execute a command or series of commmands on a remote host"""

        self._responses.flush()

        commands = to_list_of_commands(commands)

        responses = self._sendall(commands, **kwargs) or []

        if not responses:
            for command in commands:
                response = None
                error = None
                try:
                    response = self._send(command, **kwargs)
                except ExecuteFailed as exc:
                    error = exc.message
                responses.append((response, error))
                #if error:
                #    break

        if not responses:
            raise NotImplementedError(("_send or _sendall must be defined in "
                                       "subclass"))

        for command, response in zip(commands, responses):
            if isinstance(response, basestring):
                response = (response, None)
            self._responses.append((command,) + response)

        return self._responses

    def _handle_respones(self, commands, responses):
        """fill responses from two lists of commands and responses"""

    def filter_responses(self, value=""):
        """Filter to response to those commands that match the pattern"""
        filtered = []
        for response in self._responses:
            if re.search(value, str(response.command), re.I):
                filtered.append(response)
        return filtered

def _load_protocol(protocol_name):
    """Load protocol module from name"""
    import importlib
    path = ".protocols." + protocol_name
    _class_name = re.sub(r"_", "", protocol_name.title())
    module = importlib.import_module(path, package="arcomm")
    # Finally, we retrieve the Class
    return getattr(module, _class_name)

def factory_connect(host, creds, protocol=None, timeout=None, **kwargs):
    """Proxy funcion to load and instantiate protocols"""

    protocols = protocol or ARCOMM_DEFAULT_PROTOCOL
    # coerce protocol into a list
    protocols = to_list(protocols)

    timeout = timeout or ARCOMM_DEFAULT_TIMEOUT

    error = None
    for _protocol in protocols:
        try:
            _protocol_cls = _load_protocol(_protocol)
            _obj = _protocol_cls(host, creds, timeout, **kwargs)
            _obj.connect()
            return _obj
        except ConnectFailed as exc:
            error = exc.message
    message = "Failed to connect to host with error: {}".format(error)
    raise ConnectFailed(message)
