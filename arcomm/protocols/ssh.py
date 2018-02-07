# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""SSH adapter module"""

# from __future__ import (absolute_import, division, print_function,
#                         unicode_literals)

import json
import re
import socket
import time

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from arcomm.protocols.protocol import BaseProtocol
from arcomm.exceptions import ConnectFailed, ExecuteFailed, \
                              AuthenticationFailed,  AuthorizationFailed, \
                              ProtocolException
from arcomm.command import Command
from arcomm.util import to_list

try:
    import paramiko
    from paramiko.ssh_exception import SSHException
except ImportError:
    raise ProtocolException("paramiko is required for SSH connections")

from contextlib import ExitStack

class Ssh(BaseProtocol):
    """SSH class for interacting with Arista switches"""

    def __init__(self):

        # default port for ssh connections
        self._port = 22

        # default timeout
        self._timeout = 30

        # password prompt expected when authorizing
        self._password_re = [
            re.compile(r"[\r\n]?password: ?$", re.I)
        ]

        # possible command prompts
        self._prompt_re = [
            # Match on examples:
            # cs-spine-2a......14:08:54#
            # cs-spine-2a[14:08:54]#
            # cs-spine-2a>
            # cs-spine-2a#
            # cs-spine-2a(s1)#
            # cs-spine-2a(s1)(config)#
            # cs-spine-2b(vrf:management)(config)#
            # cs-spine-2b(s1)(vrf:management)(config)#
            re.compile(r"[\r\n]?[\w+\-\.:\/\[\]]+(?:\([^\)]+\)){,3}(?:>|#) ?$"),
            # Match on:
            # [admin@cs-spine-2a /]$
            # [admin@cs-spine-2a local]$
            # [admin@cs-spine-2a ~]$
            re.compile(r"\[\w+\@[\w\-\.]+(?: [^\]])\] ?[>#\$] ?$"),
            # -bash-4.1#
            # #
            re.compile(r"[\r\n]\-?(?:bash)?(?:\-\d\.\d)? ?[>#\$] ?$")
        ]

        # possible error message patterns
        self._error_re = [
            re.compile(r"% ?Error"),
            re.compile(r"^% \w+", re.M),
            re.compile(r"% ?Bad secret"),
            re.compile(r"invalid input", re.I),
            re.compile(r"(?:incomplete|ambiguous) command", re.I),
            re.compile(r"connection timed out", re.I),
            re.compile(r"[^\r\n]+ not found", re.I),
            re.compile(r"'[^']' +returned error code: ?\d+"),
            re.compile(r"[^\r\n]\/bin\/(?:ba)?sh")
        ]

        self._banner = None
        self._ssh = None
        self._channel = None

    def _clean_response(self, command, response):
        cleaned = []
        for line in response.splitlines():
            if line.startswith(str(command)):
                continue
            if self._handle_prompt(line):
                continue

            if re.match(r'\x1b[^=]*=', line):
                continue

            cleaned.append(line)

        return '\n'.join(cleaned)

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

        re_type = type(re.compile(r'^$'))

        prompt = to_list(prompt)
        answer = to_list(answer)

        if len(prompt) != len(answer):
            raise ValueError(("Lists of prompts and answers have different "
                              "lengths"))

        for _prompt, _answer in zip(prompt, answer):
            if not isinstance(_prompt, re_type):
                _prompt = re.compile(_prompt)

            match = _prompt.search(response)
            if match:
                self._channel.send(_answer + '\r')

    def _handle_prompt(self, response):
        """look for cli prompt"""
        for regex in self._prompt_re:
            match = regex.search(response)
            if match:
                return True

    def authorize(self, password, username=None):
        """Authorize the session"""
        command = Command('enable', prompt=self._password_re, answer=password)

        try:
            response = self._send(command)
        except ExecuteFailed as exc:
            raise AuthorizationFailed(str(exc))

    def close(self):
        """close the session"""
        self._ssh.close()

    def connect(self, host, creds, **kwargs):
        """Connect to a host and invoke the shell.  Returns nothing """

        options = kwargs

        timeout = options.get('timeout')
        if timeout:
            self._timeout = timeout

        port = options.get('port') or self._port

        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self._ssh.connect(host, port, username=creds.username,
                         password=creds.password, timeout=timeout,
                         look_for_keys=False)

        except paramiko.AuthenticationException as exc:
            raise AuthenticationFailed(str(exc))
        except (socket.timeout, SSHException, IOError) as exc:
            raise ConnectFailed(str(exc))

        # we must invoke a shell, otherwise session commands like 'enable',
        # 'terminal width', etc. won't stick
        channel = self._ssh.invoke_shell()
        channel.settimeout(self._timeout)
        self._channel = channel

        # capture login banner and clear any login messages
        self._banner = self._send(Command('\r'))

        # don't die if these commands aren't available
        try:
            self.send([Command('terminal length 0'),
                       Command('terminal dont-ask')])
        except ExecuteFailed:
            pass

    def send(self, commands, **kwargs):
        """Send a series of commands to the device"""
        responses = []

        # 0 if all goes well.  set to 1 on error
        status_code = 0

        timeout = kwargs.get('timeout')

        # temporarily set channel timeout.  ExitStack will restore the original
        # value within this context
        with ExitStack() as stack:

            if timeout and time != self._timeout:
                stack.callback(self._channel.settimeout, self._timeout)
                self._channel.settimeout(timeout)


            for command in commands:
                errored = None
                response = None
                if status_code == 0:
                    try:
                        response = self._send(command)
                    except ExecuteFailed as exc:
                        response = str(exc)
                        errored = True
                        status_code = 1
                        status_message = response
                responses.append([command, response, errored])

        return responses, status_code, ""

    def _send(self, command):
        """Sends a command to the remote device and returns the response"""

        buff = StringIO()

        errored_response = None

        self._channel.sendall(str(command) + '\r')
        # wait for channel to be recv_ready (only seems to be a problem in py3)
        while not self._channel.recv_ready():
            # waiting for channel to be recv_ready...
            time.sleep(.01)

        while True:
            try:
                response = self._channel.recv(1024).decode("utf-8")
            except socket.timeout:
                message = "% Timed out while running: {}".format(command)
                raise ExecuteFailed(message)

            buff.write(response)
            place = buff.tell() - 150
            if place < 0:
                place = 0
            buff.seek(place)
            window = buff.read()

            if self._handle_errors(window):
                errored_response = buff.getvalue()

            # deal with interactive input
            self._handle_input(window, command.prompt, command.answer)

            if self._handle_prompt(window):
                data = buff.getvalue()
                data = self._clean_response(command, data)
                if errored_response:
                    raise ExecuteFailed(errored_response)
                else:
                    return (data)
