# -*- coding: utf-8 -*-

# Copyright (c) 2017 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from arcomm.exceptions import AuthenticationFailed, ConnectFailed, ExecuteFailed
from arcomm.protocols.protocol import BaseProtocol
from arcomm.protocols import eapilib
from arcomm.util import zipnpad

from arcomm.command import Command

def prepare_commands(commands):
    """converts commands to Eapi formatted dicts"""

    formatted = []
    for command in commands:
        answer = command.answer or ""
        command = command.cmd.strip()

        formatted.append({"cmd": command, "input": answer})

    return formatted

class Eapi(BaseProtocol):

    def __init__(self):
        self._session = None
        self._authorize = None

    def close(self):
        self._session.logout()

    def connect(self, host, **kwargs):
        transport = kwargs.get("transport") or "http"
        # cert=None, port=None, auth=None,
        #              protocol="http", timeout=(5, 300), verify=True
        sess_args = {}
        if "cert" in kwargs:
            sess_args["cert"] = kwargs["cert"]
        elif "creds" in kwargs:
            sess_args["auth"] = kwargs["creds"].auth

        if "port" in kwargs:
            sess_args["port"] = kwargs["port"]

        if "timeout" in kwargs:
            sess_args["timeout"] = kwargs["timeout"]

        if "verify" in kwargs:
            sess_args["verify"] = kwargs["verify"]

        self._session = eapilib.Session(host, protocol=transport,
                                        **sess_args)

        if self._session.auth:
            try:
                self._session.login()
            except eapilib.EapiAuthenticationFailure as exc:
                raise AuthenticationFailed(str(exc))
            except eapilib.EapiError as exc:
                raise ConnectFailed(str(exc))

    def send(self, commands, **kwargs):

        result = None
        results = []
        status_code = 0
        status_message = None

        encoding = kwargs.get("encoding", kwargs.get("format", "text"))
        timestamps = kwargs.get("timestamps", False)
        timeout = kwargs.get("timeout", None)

        if self._authorize:
            commands = [self._authorize] + commands

        try:
            data = self._session.execute(prepare_commands(commands),
                                         format=encoding,
                                         timestamps=timestamps,
                                         timeout=timeout)
        except eapilib.EapiError as exc:
            raise ExecuteFailed(str(exc))

        if "error" in data:
            status_code = data["error"]["code"]
            status_message = data["error"]["message"]
            result = data["error"].get("data", [])
        else:
            result = data["result"]

        for command, response in zipnpad(commands, result):
            errored = None
            output = None

            if result:
                if encoding == "text":
                    output = response["output"]
                else:
                    output = response

                if "errors" in response:
                    errored = True
                else:
                    errored = False

            results.append([command, output, errored])

        if len(results) > 1 and self._authorize:
            results.pop(0)

        return (results, status_code, status_message)

    def authorize(self, password, username=None):
        self._authorize = Command({"cmd": "enable", "input": password})
