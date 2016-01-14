# -*- coding: utf-8 -*-
"""Store responses"""

import json
import re

from arcomm.util import to_list
from arcomm.exceptions import ExecuteFailed

# _status = {
#     0: ('ok',),
#     1: ('failed',)
# }

class Response(object):
    """Store a single response"""
    def __init__(self, command, output, errored=False):
        self.command = command
        self.output = output
        self.errored = errored

    def __contains__(self, item):
        return item in self._output

    def __getitem__(self, sl):
        return str(self.output)[sl]

    def __str__(self):
        """return the data from the response as a string"""
        return str(self.output)

class ResponseStore(object):
    """List-like object for storing responses"""

    def __init__(self, host, **kwargs):

        #
        self._store = []

        #
        self.host = host

        #
        self.status = None

        #
        self._keywords = kwargs

    def __iter__(self):
        return iter(self._store)

    def __getitem__(self, item):
        return self._store[item]

    def __str__(self):

        str_ = ""
        for response in self._store:
            str_ += "{}#{}\n{}\n".format(self.host, str(response.command).strip(),
                                       response.output)
        return str_

    def __contains__(self, item):
        """allow string searches on all responses"""
        return item in self.__str__()

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
            item = Response(*item)

        if item.errored:
            self.status = 'failed'

        self._store.append(item)

    def filter(self, value=""):
        """filter responses to those commands that match the pattern"""
        filtered = []
        for response in self._store:
            if re.search(value, str(response.command), re.I):
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
        first_error = self.errored()[0]
        if first_error:
            raise ExecuteFailed(first_error)
