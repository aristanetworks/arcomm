# -*- coding: utf-8 -*-
"""Base module for protocol adapters"""

import abc

class BaseProtocol(object):
    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def connect(self, host, creds, **kwargs):
        pass

    @abc.abstractmethod
    def send(self, commands, **kwargs):
        pass

    @abc.abstractmethod
    def authorize(self, password, username):
        pass
