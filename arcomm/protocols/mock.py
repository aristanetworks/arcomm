# -*- coding: utf-8 -*-
# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import json
import warnings

from arcomm.exceptions import (ConnectFailed, ExecuteFailed,
                               AuthenticationFailed,  AuthorizationFailed,
                               ProtocolException)
from arcomm.protocols.protocol import BaseProtocol
from arcomm.command import Command

import platform
import datetime
import time

def _show_version(authorized):
    return " ".join(platform.uname())

def _show_clock(authorized):
    return datetime.datetime.utcnow().isoformat()

def _configure(authorized):
    pass

def _show_restricted(authorized):
    if not authorized:
        raise ValueError('Command not authorized')

    return 'Drink more Ovaltine'

def _end(authorized):
    pass

def _sleep(authorized):
    time.sleep(5)

COMMANDS = {
# 'show': {
    #     'version': " ".join(platform.uname()),
    #     'clock:': datetime.datetime.utcnow().isoformat(),
    # }
    'show version': _show_version,
    'show clock': _show_clock,
    'show restricted': _show_restricted,
    'configure': _configure,
    'end': _end,
    'sleep': _sleep
}

class Mock(BaseProtocol):

    def __init__(self):
        # ghost connection
        self._connected = False
        self._authorized = False

    def authorize(self, password, username):
        if 'bad' in password:
            raise AuthorizationFailed('Invalid authorization')

        self._auhorized = True

    def close(self):
        self._connected = False

    def connect(self, host, creds, **kwargs):
        if (creds.password and 'bad' in creds.password) or 'bad' in creds.username:
            raise AuthenticationFailed('Invalid username/password')

        self._connected = True

    def send(self, commands, **kwargs):

        results = []

        for command in commands:
            if command.cmd in COMMANDS:
                try:
                    results.append(COMMANDS[command.cmd](self._authorized))
                except Exception as exc:
                    raise ExecuteFailed('Command failed: {}'.format(exc))
            else:
                raise ExecuteFailed('Invalid command {}'.format(command.cmd),
                                    command)

        return results
