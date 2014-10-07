# -*- coding: utf-8 -*-
"""Protocol adapter for CAPI aka eAPI aka JSON-RPC"""

import jsonrpclib
import socket
from ..command import Command
from ..protocol import Protocol
from ..exceptions import ExecuteFailed, ConnectFailed

def _format_commands(commands):
    """converts commands to CAPI formatted dicts"""
    formatted = []
    for command in commands:
        _cmd = str(command).strip()
        _answer = command.answer or ""
        formatted.append(dict(cmd=_cmd, input=_answer))
    return formatted

# wrapper for jsonrpclib, works with Arista switches over http or https?
class Capi(Protocol):
    """Protocol adapter for CAPI aka eAPI aka JSON-RPC"""

    _url = None
    _format = "text"
    _transport = "http"
    _enable = None
    _marker = ">"

    @property
    def url(self):
        """Return the internal '_url' attr"""
        return self._url

    @property
    def format(self):
        """Return the internal '_format' attr"""
        return self._format

    @property
    def transport(self):
        """Return the internal '_transport' attr"""
        return self._transport

    def _seturl(self, host, creds, transport):
        """Sets the JSON-RPC URL"""
        url = ("{transport}://{creds.username}:{creds.password}@{host}/"
               "command-api")
        url = url.format(host=host, creds=creds, transport=transport)
        self._url = url

    def _on_initialize(self, **kwargs):
        """Setup protocol specific attributes"""

        transport = kwargs.get("transport") or self._transport
        self._format = kwargs.get("output_format") or self._format
        self._seturl(self.host, self.creds, transport)

    def _authorize(self, secret):
        """Authorize the 'session'"""
        self._enable = Command("enable", answer=secret)
        self._marker = "#"

    def _connect(self, host, creds):
        """Make the connection.  Force a test by running 'help' on the switch"""

        try:
            connection = jsonrpclib.Server(self.url)

            # since JSON-RPC doesn't connect right away, we will run a test
            # command
            self._connection = connection
            self.execute("show clock")
            return connection
        except IOError as exc:
            raise ConnectFailed(exc.message)

    def _format_response(self, commands, responses):
        """Format the command response to look like an interactive session"""
        formatted = []
        # make a fake prompt
        prompt = "{} (command-api){}".format(self.host, self._marker)
        for command, response in zip(commands, responses):
            command = command.get("cmd")
            response = "{}{}\n{}".format(prompt, command, response)
            formatted.append(response)
        return formatted

    def _sendall(self, commands):
        """Sends all commands at once since CAPI doesn't deal with sessions"""
        if self._enable:
            commands.insert(0, self._enable)
        commands = _format_commands(commands)
        try:
            responses = self.connection.runCmds(1, commands, self.format)
            responses = [_response["output"] for _response in responses]
            responses = self._format_response(commands, responses)
            return responses
        except jsonrpclib.jsonrpc.ProtocolError as exc:
            raise ExecuteFailed("Send failed: {}".format(exc.message))

