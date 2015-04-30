# -*- coding: utf-8 -*-
"""Command module.  stores command and any prompts or answers it may require"""

import collections
from .util import to_list

class Command(collections.MutableMapping):
    """Object to store command and any prompts or answers it may require"""

    def __init__(self, cmd, prompt=None, answer=None):
        if isinstance(cmd, dict):
            prompt = cmd.get("prompt")
            answer = cmd.get("answer")
            cmd = cmd.get("cmd")
        assert isinstance(cmd, basestring), "cmd must be a string"
        
        self._store = dict()
        self.update(dict(cmd=cmd, prompt=to_list(prompt), answer=answer))

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
        return self._store.get("cmd")
    expression = command = cmd

    @property
    def prompt(self):
        """Returns the prompt(s)"""
        return self._store.get("prompt")

    @property
    def answer(self):
        """Returns the answer for the prompt"""
        return self._store.get("answer")

    def __str__(self):
        return self.cmd

    def __repr__(self):
        return str(dict(cmd=self.cmd, prompt=self.prompt, answer=self.answer))
