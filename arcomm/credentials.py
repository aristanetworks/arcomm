# -*- coding: utf-8 -*-
"""Credentials module for holding username, password, keys, and enable
passwords
"""

import collections
import getpass

class Creds(collections.MutableMapping):
    """Credentials class stores username, passwords, keys"""
    def __init__(self, username=None, password=None, authorize_password=None,
                 private_key=None):
        self._creds = dict()

        if not username:
            username = getpass.getuser()
            _prompt = "Please enter username [{}]:".format(username)
            username = raw_input(_prompt) or username

        if password is None:
            password = getpass.getpass('Password for %s: ' % username)

        _updates = dict(username=username, password=password,
                        authorize_password=authorize_password,
                        private_key=private_key)

        self.update(_updates)

    def __getitem__(self, key):
        return self._creds[key]

    def __setitem__(self, key, value):
        self._creds[key] = value

    def __delitem__(self, key):
        del self._creds[key]

    def __iter__(self):
        return iter(self._creds)

    def __len__(self):
        return len(self._creds)

    def __repr__(self):
        """Do show the password when logging"""
        _repr = "{}(username = '{}', password = '****')"
        return _repr.format(self.__class__, self.username)

    def __str__(self):
        return str(self._creds)

    @property
    def username(self):
        """returns username"""
        return self.get("username")

    @property
    def password(self):
        """returns authentication password"""
        return self.get("password")

    @property
    def authorize_password(self):
        """returns authorization password"""
        return self.get("authorize_password")

    @property
    def private_key(self):
        """returns path to private-key"""
        return self.get("private_key")

    @property
    def uripart(self):
        """Return a string containg: <username>:<password> for use with a URI"""
        parts = [self.username]
        if self.password:
            parts.append(self.password)
        return ":".join(parts)
    uri = uripart
