# -*- coding: utf-8 -*-
"""SSH adapter module"""

import re
import socket
from StringIO import StringIO
from ..protocol import Protocol
from ..exceptions import ConnectFailed, ExecuteFailed, AuthenticationFailed, \
                         AuthorizationFailed, ProtocolException
from ..command import Command
from ..util import to_list
import json

try:
    import paramiko
except ImportError:
    ProtocolException("paramiko is required for SSH connections")

class Ssh(Protocol):
    """SSH protocol adapter"""

    _port = 22
    _channel = None
    _banner = ""
    _password_re = [
        re.compile(r"[\r\n]?password: ?$", re.I)
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
        re.compile(r"% ?Error"),
        re.compile(r"^% \w+", re.M),
        re.compile(r"% ?Bad secret"),
        re.compile(r"invalid input", re.I),
        re.compile(r"(?:incomplete|ambiguous) command", re.I),
        re.compile(r"connection timed out", re.I),
        re.compile(r"[^\r\n]+ not found", re.I),
        re.compile(r"'[^']' +returned error code: ?\d+"),
        re.compile(r"[^\r\n]\/bin\/(?:ba)?sh", )
    ]

    def _on_initialize(self, **kwargs):
        self._port = kwargs.get("port") or self._port

    def _authorize(self, secret):
        """Authorize the connection"""
        command = Command("enable", prompt=self._password_re, answer=secret)
        response = self.execute([command])
        if response[0].errors:
            raise AuthorizationFailed(response[0].errors.pop())

    def _connect(self, host, creds):
        """Connect to a remote host"""
        _ssh = paramiko.SSHClient()
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            _ssh.connect(host, self._port, username=creds.username,
                         password=creds.password, timeout=self.timeout)
        except paramiko.AuthenticationException as exc:
            raise AuthenticationFailed(exc.message)
        except socket.timeout as exc:
            raise ConnectFailed(str(exc))
        except IOError as exc:
            raise ConnectFailed("{}: {}".format(exc[0], exc[1]))

        _channel = _ssh.invoke_shell()
        _channel.settimeout(self.timeout)

        self._channel = _channel
        # might need to read this later?
        self._banner = self._send(Command("\n"))
        return _ssh

    def _send(self, command, encoding="text"):
        """Sends a command to the remote device and returns the response"""

        buff = StringIO()
        errored_response = ""

        send = str(command)
        if encoding == "json":
            send = send + " | json"
        self._channel.sendall(send + '\r')

        while True:
            response = self._channel.recv(200)

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
                    response = buff.getvalue()

                    response = self._clean_response(command, response)

                    return json.loads(response) if encoding == "json" else response

    def _clean_response(self, command, response):
        cleaned = []
        for line in response.splitlines():
            if line.startswith(str(command)):
                continue
            if self._handle_prompt(line):
                continue

            cleaned.append(line)
        return "\n".join(cleaned)


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
        answer = to_list(answer)
        for _pr, _ans in zip(prompt, answer):
            print "PROMPT", _pr, _ans
            match = _pr.search(response)
            if match:
                self._channel.send("{}\n".format(_ans))

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
