# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Credentials module for holding username, password, keys, and enable
passwords
"""

import collections
import getpass

def mkcreds(username, **kwargs):
    return BasicCreds(username=username, **kwargs)

# make a list of creds for sessions to try?
def credentials_from_list(creds):
    pass

class BaseCreds(collections.Mapping):
    """Credentials class stores username, passwords, keys"""
    def __init__(self, **kwargs):
        self._creds = dict(**kwargs)

    def __getitem__(self, name):
        return self._creds[name]

    def __iter__(self):
        return iter(self._creds)

    def __len__(self):
        return len(self._creds)

    def __str__(self):
        return str(self._creds)

class BasicCreds(BaseCreds):

    def __init__(self, username, password="", **kwargs):
        super(BasicCreds, self).__init__(username=username, password=password,
            **kwargs)

    @property
    def username(self):
        return self._creds['username']

    @property
    def password(self):
        return self._creds['password']

    def __repr__(self):
       """Do show the password when logging"""
       _repr = "{}(username = '{}', password = '****')"
       return _repr.format(self.__class__, self.username)

    @property
    def auth(self):
        return (self.username, self.password)

class Creds(BasicCreds):
    pass
