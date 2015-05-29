# -*- coding: utf-8 -*-
"""Eapi adpter"""
from ._eapi import _Eapi, _EapiException
from ..protocol import Protocol
from ..exceptions import ExecuteFailed

def _format_commands(commands):
    """converts commands to Eapi formatted dicts"""
    formatted = []
    for command in commands:
        _cmd = str(command).strip()
        _answer = command.answer or ""
        formatted.append(dict(cmd=_cmd, input=_answer))
    return formatted

class Eapi(Protocol):
    """Wrapper class for JSON-RPC API"""
    _marker = ">"
    _use_ssl = False
    _port = 80
    def _on_initialize(self, **kwargs):
        """Setup protocol specific attributes"""
        pass

    def _authorize(self, secret):
        """Authorize the 'session'"""
        self.connection.enable()
        self._marker = "#"

    def _connect(self, host, creds):
        """returns a _Eapi object, no connection is made at this time"""
        return _Eapi(host, username=creds.username, password=creds.password,
                     enable=creds.authorize_password, use_ssl=self._use_ssl,
                     port=self._port) #, encoding=self._encoding,
                     #timestamps=self._timestamps)

    # def _format_response(self, commands, responses):
    #     """Format the command response to look like an interactive session"""
    #
    #     formatted = []
    #     # make a fake prompt
    #     prompt = "{} (command-api){}".format(self.host, self._marker)
    #
    #     for command, response in zip(commands, responses):
    #         command = command.get("cmd")
    #         response = "{}{}\n{}".format(prompt, command, response)
    #         formatted.append(response)
    #     return formatted

    def _sendall(self, commands, encoding="text", timestamps=False):
        """Send all commands in one request. Eapi track conext (enabled? or
        configured?, etc...)"""
        commands = _format_commands(commands)
        try:
            response = self.connection.execute(commands, encoding=encoding, timestamps=timestamps)
        except _EapiException as exc:
            raise ExecuteFailed("Send failed: {}".format(exc.message))

        if encoding == "text":
            responses = [_res["output"] for _res in response["result"]]
        else:
            responses = response["result"]
        return responses