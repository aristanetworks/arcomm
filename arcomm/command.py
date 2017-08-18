# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Command module.  stores command and any prompts or answers it may require"""
from past.builtins import str, basestring
import collections
import re
from arcomm.util import to_list


def mkcmd(command, prompt=None, answer=None):
    return Command(command, prompt=prompt, answer=answer)

command_from_dict = cmd = mkcmd

def commands_from_list(commands):
    """Converts a command or list of commands to a list of Command objects"""
    commands = to_list(commands)
    cmdlist = []
    for cmd in commands:
        if not isinstance(cmd, Command):
            if re.search("^(!|#)", cmd) or re.search("^\s*$", cmd):
                continue
            cmd = Command(cmd.strip())
        cmdlist.append(cmd)
    return cmdlist

class Command(collections.MutableMapping):
    """Object to store command and any prompts or answers it may require"""

    def __init__(self, cmd, prompt=None, answer=None):
        if isinstance(cmd, dict):
            prompt = cmd.get("prompt")
            answer = cmd.get("answer", cmd.get('input', ''))
            cmd = cmd.get("cmd", cmd.get('command'))

        if not isinstance(cmd, basestring):
            raise ValueError("'cmd' must be a string")

        self._store = dict()
        self.update(dict(cmd=cmd, prompt=prompt, answer=answer))

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    @property
    def cmd(self):
        """Returns command sting"""
        return self._store.get('cmd')

    expression = command = cmd

    @property
    def prompt(self):
        """Returns the prompt(s)"""
        return self._store.get('prompt')

    @property
    def answer(self):
        """Returns the answer for the prompt"""
        return self._store.get('answer')

    input = answer

    def __str__(self):
        return self.cmd

    def __repr__(self):
        return str(dict(cmd=self.cmd, prompt=self.prompt, answer=self.answer))
