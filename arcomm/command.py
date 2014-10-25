# -*- coding: utf-8 -*-
"""Command module.  stores command and any prompts or answers it may require"""

import collections
from .util import to_list

class Command(collections.MutableMapping):
    """Object to store command and any prompts or answers it may require"""

    def __init__(self, expression, prompt=None, answer=None):

        assert isinstance(expression, basestring), "expression must be a string"

        self._store = dict()
        prompt = to_list(prompt)
        updates = dict(expression=expression, prompt=prompt, answer=answer)
        self.update(updates)

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
    def expression(self):
        """Returns command sting"""
        return self._store.get("expression")
    command = expression

    @property
    def prompt(self):
        """Returns the prompt(s)"""
        return self._store.get("prompt")

    @property
    def answer(self):
        """Returns the answer for the prompt"""
        return self._store.get("answer")

    def __str__(self):
        return self.expression

    def __repr__(self):
        _data = dict(expression=self.expression, prompt=self.prompt,
                     answer=self.answer)
        return str(_data)
