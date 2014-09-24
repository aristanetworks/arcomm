# -*- coding: utf-8 -*-
# Copyright (c) 2014 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
"""EOS CLI wrapper.  Allow scripts to be run directly from the switch"""
import os
import subprocess
from ..protocol import Protocol

class Cli(Protocol):
    """EOS CLI protocol adapter"""
    _privilege_level = 1

    _fastcli = "/usr/bin/FastCli"
    def _on_initialize(self, **kwargs):
        if not os.path.exists(self._fastcli):
            raise ValueError("{} not found. Is this EOS?".format(self._fastcli))

    def _authorize(self, secret):
        self._privilege_level = 15

    def _connect(self, host, creds):
        pass

    def _send(self, command):
        """Send to command to the Cli"""
        _fastcli = self._fastcli
        _privilege_level = self._privilege_level
        command = "{} -p {} -c {}".format(_fastcli, _privilege_level, command)
        command = command.split(" ")
        response = subprocess.check_output(command, stderr=subprocess.STDOUT)
        return response
