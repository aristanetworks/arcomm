# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Store responses"""

import json
import re
import time
import yaml
import arcomm
from arcomm.util import to_list, indentblock
from arcomm.exceptions import ExecuteFailed

_SUBSCRIBERS = []

def subscribe(callback):
    """Adds a global subscriber"""
    if not hasattr(callback, '__call__'):
        raise TypeError("callbeck must be callable")

    _SUBSCRIBERS.append(callback)

def unsubscribe(callback):
    callback = to_list(callback)
    global _SUBSCRIBERS
    _SUBSCRIBERS = [cb for cb in _SUBSCRIBERS if cb not in callback]

def get_subscribers():
    """Get all global subs"""
    return _SUBSCRIBERS

class Response(object):
    """Store a single response"""

    def __init__(self, parent, command, output, errored=None):

        self.parent = parent
        self.command = command
        self.output = output
        self.errored = errored

        self.created_at = time.time()

    def __contains__(self, item):
        return item in str(self._output)

    def __getitem__(self, item):
        if isinstance(item, slice) or isinstance(item, int):
            return str(self.output)[item]
        else:
            return self.output[item]

    def __str__(self):
        """return the data from the response as a string"""
        return str(self.output)

    def to_dict(self):
        return {
            "command": self.command.to_dict(),
            "output": self.output,
            "errored": self.errored
        }

class ResponseStore(object):
    """List-like object for storing responses"""

    def __init__(self, session, **kwargs):

        self._store = []
        self.session = session
        self.status = 'ok'
        self._keywords = kwargs

        self._subscribers = []

    def __iter__(self):
        return iter(self._store)

    def __getitem__(self, item):
        return self._store[item]

    def __str__(self):
        return self.to_yaml()

    def to_dict(self):
        result = {'host': self.host, 'status': self.status, 'commands': []}

        for response in self:

            result['commands'].append(response.to_dict())

        return result

    @property
    def host(self):
        return self.session.hostname

    def to_yaml(self):
        doc = ['host: {}'.format(self.host)]
        doc.append('status: {}'.format(self.status))
        doc.append('commands:')

        for r in self:

            if isinstance(r.command, arcomm.command.Command):
                doc.append('  - command: {}'.format(r.command.cmd))
                if r.command.prompt:
                    doc.append('    prompt: {}'.format(r.command.prompt))
                if r.command.answer:
                    doc.append('    answer: {}'.format(r.command.answer))

            else:
                doc.append('  - command: {}'.format(r.command))

            if r.errored is None:
                errored = 'skipped'
            else:
                errored = 'failed' if r.errored else 'ok'

            doc.append('    status: {}'.format(errored))
            doc.append('    output: |')

            doc.append(indentblock(str(r.output), spaces=6))

        return '\n'.join(doc)

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4, separators=(',', ': '))

    def __repr__(self):
        return '<{} [{}]>'.format(self.__class__.__name__, self.status)

    def __contains__(self, item):
        """allow string searches on all responses"""
        return item in self.__str__()

    def _notify(self, response):

        subscribers = get_subscribers() + self._subscribers

        for callback in subscribers:
            callback(response)

    @property
    def responses(self):
        """returns the response data from each response"""
        return [response.output for response in self._store]

    @property
    def commands(self):
        """returns the command from each response"""
        return [response.command for response in self._store]

    def append(self, item):
        """adds a response item to the list"""

        if not isinstance(item, Response):
            item = Response(self, *item)

        if item.errored:
            self.status = 'failed'

        self._notify(item)

        self._store.append(item)

    def filter(self, value=""):
        """filter responses to those commands that match the pattern"""
        filtered = []
        for response in self._store:
            if re.search(value, str(response.command.cmd), re.I):
                filtered.append(response)
        return filtered

    def errored(self):
        return [response for response in self if response.errored]

    def last(self):
        """returns the last response item"""
        return self._store[-1]

    def flush(self):
        """emptys the responses"""
        self._store = list()

    def splitlines(self):
        return self.__str__().splitlines()

    def raise_for_error(self):
        errors = self.errored()
        if errors:
            raise ExecuteFailed(errors[0])

    def subscribe(self, callback):
        self._subscribers.append(callback)
