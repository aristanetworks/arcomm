# -*- coding: utf-8 -*-

# Copyright (c) 2017 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from arcomm.exceptions import AuthenticationFailed, ConnectFailed, ExecuteFailed
from arcomm.protocols.protocol import BaseProtocol
from arcomm.util import zipnpad
from arcomm.command import Command
from pprint import pprint
import eapi as eapi_

eapi_.SSL_WARNINGS = False

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

        self._session = eapi_.Session(host, transport=transport,
                                        **sess_args)

        if self._session.auth:
            try:
                self._session.login()
            except eapi_.EapiAuthenticationFailure as exc:
                raise AuthenticationFailed(str(exc))
            except eapi_.EapiError as exc:
                raise ConnectFailed(str(exc))

    def send(self, commands, **kwargs):

        # result = None
        results = []

        response = None

        status_code = 0
        status_message = None

        encoding = kwargs.get("encoding", kwargs.get("format", "text"))
        timestamps = kwargs.get("timestamps", False)
        timeout = kwargs.get("timeout", None)

        if self._authorize:
            commands = [self._authorize] + commands

        try:
            response = self._session.execute(prepare_commands(commands),
                                         encoding=encoding,
                                         timestamps=timestamps,
                                         timeout=timeout)

        except eapi_.EapiError as exc:
            raise ExecuteFailed(str(exc))

        status_code = response.code
        status_message = response.message

        for command, result in zipnpad(commands, response.result):
            errored = None

            if result:
                if "errors" in result.dict:
                    errored = True
                else:
                    errored = False

            results.append([command, result.text, errored])

        if len(results) > 1 and self._authorize:
            results.pop(0)

        return (results, status_code, status_message)

    def authorize(self, password, username=None):
        self._authorize = Command({"cmd": "enable", "input": password})
