# -*- coding: utf-8 -*-
"""Base module for protocol adapters"""

class BaseProtocol(object):

    def close(self):
        raise NotImplementedError()

    def connect(self, host, creds, options):
        raise NotImplementedError()

    def send(self, command):
        raise NotImplementedError()

    def super(self, creds=('', '')):
        raise NotImplementedError()
