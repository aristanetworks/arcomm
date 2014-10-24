# -*- coding: utf-8 -*-

from _capi import _Capi, _CapiException
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

class Capi(Protocol):
    
    _marker = ">"
    _use_ssl = False
    _port = 80
    _encoding = "text"
    _timestamps = False
    def _on_initialize(self, **kwargs):
        """Setup protocol specific attributes"""
        # transport = kwargs.get("transport") or self._transport
        # self._format = kwargs.get("output_format") or self._format
        # self._seturl(self.host, self.creds, transport)

    def _authorize(self, secret):
        """Authorize the 'session'"""
        self.connection.enable()
        self._marker = "#"

    def _connect(self, host, creds):
        
        self._conn = _Capi(host, username=creds.username,
                            password=creds.password,
                            enable=creds.authorize_password,
                            use_ssl=self._use_ssl, port=self._port,
                            encoding=self._encoding, timestamps=self._timestamps)
        return self._conn
        
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
        commands = _format_commands(commands)
        try:
            response = self.connection.execute(commands)
        except _CapiException as exc:
            raise ExecuteFailed("Send failed: {}".format(exc.message))
        
        response = [_res["output"] for _res in response["result"]]
        response = self._format_response(commands, response)
        return response