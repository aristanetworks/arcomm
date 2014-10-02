# -*- coding: utf-8 -*-
"""SSH adapter module"""

import re
import socket
import paramiko
from paramiko import AuthenticationException
from StringIO import StringIO
from ..protocol import Protocol
from ..exceptions import ConnectFailed, ExecuteFailed, Timeout, \
                         AuthenticationFailed
from ..command import Command
from ..util import to_list

class Ssh(Protocol):
    """SSH protocol adapter"""

    _port = 22
    _channel = None
    _banner = ""
    _password_re = [
        re.compile(r'[\r\n]?password: ?$', re.I)
    ]

    _prompt_re = [
        # Match on:
        # cs-spine-2a......14:08:54#
        # cs-spine-2a>
        # cs-spine-2a#
        # cs-spine-2a(s1)#
        # cs-spine-2a(s1)(config)#
        # cs-spine-2b(vrf:management)(config)#
        # cs-spine-2b(s1)(vrf:management)(config)#
        re.compile(r"[\r\n]?[\w+\-\.:\/]+(?:\([^\)]+\)){,3}(?:>|#) ?$"),
        # Match on:
        # [admin@cs-spine-2a /]$
        # [admin@cs-spine-2a local]$
        # [admin@cs-spine-2a ~]$
        # -bash-4.1#
        re.compile(r"\[\w+\@[\w\-\.]+(?: [^\]])\] ?[>#\$] ?$")
    ]

    _error_re = [
        re.compile(r'% ?Error'),
        re.compile(r'% ?Bad secret'),
        re.compile(r'invalid input', re.I),
        re.compile(r'(?:incomplete|ambiguous) command', re.I),
        re.compile(r'connection timed out', re.I),
        re.compile(r'[^\r\n]+ not found', re.I)
    ]

    def _on_initialize(self, **kwargs):
        self._port = kwargs.get("port") or self._port

    def _authorize(self, secret):
        """Authorize the connection"""
        command = Command("enable", prompt=self._password_re, answer=secret)
        self.execute([command])

    def _connect(self, host, creds):
        """Connect to a remote host"""

        _ssh = paramiko.SSHClient()
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            _ssh.connect(host, self._port, username=creds.username,
                         password=creds.password, timeout=self.timeout)
        except AuthenticationException as exc:
            raise AuthenticationFailed(exc.message)
        except IOError as e:
            raise ConnectFailed(e.message)
        
        _channel = _ssh.invoke_shell()
        _channel.settimeout(self.timeout)

        self._channel = _channel
        # might need to read this later?
        self._banner = self._send(Command("\n"))
        return _ssh

    def _send(self, command):
        """Sends a command to the remote device and returns the response"""
        
        buff = StringIO()
        errored_response = ""
        self._channel.sendall(str(command) + '\r')

        while True:
            try:
                response = self._channel.recv(200)
            except socket.timeout:
                raise Timeout("% Timeout while running: {}".format(command))

            buff.write(response)

            buff.seek(buff.tell() - 150)
            window = buff.read()

            if self._handle_errors(window):
                errored_response = buff.getvalue()

            # deal with interactive input
            self._handle_input(window, command.prompt, command.answer)

            if self._handle_prompt(window):
                if errored_response:
                    raise ExecuteFailed(errored_response)
                else:
                    return buff.getvalue()

    def _handle_errors(self, response):
        """look for errors"""

        for regex in self._error_re:
            match = regex.search(response)
            if match:
                # capture part of output that contains the error,
                # but do not raise an exception yet.  We need to make
                # sure to receive all the data from that channel
                return True
        return False

    def _handle_input(self, response, prompt, answer):
        """look for interactive prompts and send answer"""
        if prompt is None or answer is None:
            return

        prompt = to_list(prompt)

        for regex in prompt:
            match = regex.search(response)
            if match:
                self._channel.send("{}\n".format(answer))

    def _handle_prompt(self, response):
        """look for cli prompt"""
        for regex in self._prompt_re:
            match = regex.search(response)
            if match:
                return True

    def _on_connect(self):
        self.execute("terminal length 0")

    def _close(self):
        if hasattr(self.connection, "close"):
            self.connection.close()
