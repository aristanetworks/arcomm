# -*- coding: utf-8 -*-
"""Base module for protocol adapters"""

import re
import json
from .command import Command
from .util import to_list, indentblock
from .exceptions import ProtocolException, AuthorizationFailed, ConnectFailed, ExecuteFailed
DEFAULT_PROTOCOL = ["eapi", "ssh"]
DEFAULT_TIMEOUT = 30

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

class Response(object):
    """Store a single response"""
    def __init__(self, command, output, error=None):
        self._command = command
        self._output = output
        self._error = error

    @property
    def command(self):
        """Returns the command used to generate the response"""
        return self._command

    @property
    def output(self):
        """data returned from the command"""
        return self._output

    @property
    def error(self):
        return self._error

    @property
    def errors(self):
        return to_list(self.error)

    def __contains__(self, item):
        return item in self._output

    def __str__(self):
        """return the data from the response as a string"""
        return self._output

    def to_dict(self):
        return {"command": str(self.command), "output": self.output, "errors": self.errors}

class ResponseStore(object):
    """List-like object for storing responses"""
    def __init__(self):
        self._store = list()

    def __iter__(self):
        return iter(self._store)

    def __getitem__(self, item):
        return self._store[item]

    def __str__(self):
        str_ = ""
        for response in self._store:
            str_ += "#{}\n{}\n".format(str(response.command).strip(),
                                       response.output)
        return str_

    def __contains__(self, item):
        """allow string searches on all responses"""
        return item in self.__str__()

    @property
    def responses(self):
        """returns the response data from each response"""
        return [response.output for response in self._store]

    @property
    def commands(self):
        """returns the command from each response"""
        return [response.command for response in self._store]

    def append(self, item):
        """adds a response item to the list"""
        if not isinstance(item, Response):
            item = Response(*item)
        self._store.append(item)

    def filter(self, value=""):
        """filter responses to those commands that match the pattern"""
        filtered = []
        for response in self._store:
            if re.search(value, str(response.command), re.I):
                filtered.append(response)
        return filtered

    def last(self):
        """returns the last response item"""
        return self._store[-1]

    def flush(self):
        """emptys the responses"""
        self._store = list()

    def splitlines(self):
        """returns responses as a list"""
        return self.responses

    def to_dict(self):
        data = []
        for response in self._store:
            data.append(response.to_dict())
        return data

    def to_json(self, *args, **kwargs):
        return json.dumps(self.to_dict(), *args, **kwargs)

    def to_yaml(self, *args, **kwargs):
        yml = "commands:"
        for response in responses:
            yml += "  command: {}".format(response.command)
            yml += "    output: |"
            yml += indentblock(response.output, spaces=4)
            if response.error:
                yml += "    errors: |"
                yml += indentblock(response.error, spaces=4)
        return yml
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
        self._responses = ResponseStore()
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
            raise AuthorizationFailed(_message)

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
                if error:
                    break

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

def factory_connect(host, creds, protocol=None, timeout=None):
    """Proxy funcion to load and instantiate protocols"""

    protocols = protocol or DEFAULT_PROTOCOL
    # coerce protocol into a list
    protocols = to_list(protocols)

    timeout = timeout or DEFAULT_TIMEOUT

    error = None
    for _protocol in protocols:
        try:
            _protocol_cls = _load_protocol(_protocol)
            _obj = _protocol_cls(host, creds, timeout)
            _obj.connect()
            return _obj
        except ConnectFailed as exc:
            error = exc.message
    message = "Failed to connect to host with error: {}".format(error)
    raise ConnectFailed(message)
