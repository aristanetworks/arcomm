# -*- coding: utf-8 -*-
# Copyright (c) 2018 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.


"""eapilib: A Simple eAPI :ibrary

Examples:

Login/logout endpoint:

    with Session(hostaddr, protocol="http", auth=("admin", "")) as sess:
        resp = sess.execute(["show version"], format="json")
        for item in resp.iter_result():
            pprint(item)

HTTPS w/client certificate (self-signed use verify=False):

    with Session(hostaddr, protocol="https", cert=(cert, key),
                 verify=False) as sess:
        resp = sess.execute(["show version"], format="json")
        for item in resp.iter_result():
            pprint(item)
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
import requests
import urllib3
import uuid

class EapiError(Exception):
    """General eAPI failure"""
    pass

class EapiTimeoutError(EapiError):
    pass

class EapiHttpError(EapiError):
    pass

class EapiResponseError(EapiError):
    pass

class EapiAuthenticationFailure(EapiError):
    pass

class Session(object):
    """EAPI Session"""

    def __init__(self, hostaddr, auth=None, cert=None, port=None,
                 protocol="http", timeout=(5, 300), verify=True):

        # use a requests Session to manage state
        self._session = requests.Session()

        # every request should send the same headers
        self._session.headers = {"Content-Type": "application/json"}

        self.hostaddr = hostaddr

        self.auth = auth

        self.cert = cert

        self.port = port

        self.protocol = protocol

        self.timeout = timeout

        self.verify = verify

    def __enter__(self):
        if self.auth:
            self.login()
        return self

    def __exit__(self, *args):
        self.logout()
        self.close()

    @property
    def verify(self):
        return self._verify

    @verify.setter
    def verify(self, value):
        if value is False:
            urllib3.disable_warnings()
        self._verify = value

    @property
    def logged_in(self):
        if "Session" in self._session.cookies:
            return True
        return False

    def prepare_url(self, path=""):
        url = "{}://{}".format(self.protocol, self.hostaddr)

        if self.port:
            url += ":{}".format(self.port)

        return url + path

    def close(self):
        self._session.close()

    def login(self, **kwargs):
        """Session based Authentication

        """

        if not len(self.auth) == 2:
            raise ValueError("username and password auth tuple is required")

        username, password = self.auth

        payload = {"username": username, "password": password}
        resp = self.send("/login", data=payload, **kwargs)

        code = resp.status_code

        if resp.status_code == 401:
            raise EapiAuthenticationFailure(resp.text)
        elif resp.status_code == 404 or "Session" not in resp.cookies:
            # fall back to basic auth if /login is not found or Session key is
            # missing
            self.auth = (username, password)
            return
        elif not resp.ok:
            raise EapiError(resp.reason)

        self.auth = None

    def logout(self, **kwargs):
        if self.logged_in:
            return self.send("/logout", data={}, **kwargs)

    def execute(self, commands, format="text", timestamps=False, id=None,
                **kwargs):

        if not id:
            id = str(uuid.uuid4())

        params = {
            "version": 1,
            "cmds": commands,
            "format": format
        }

        # timestamps is a newer param, only include it if requested
        if timestamps:
            params["timestamps"] = timestamps

        payload = {
            "jsonrpc": "2.0",
            "method": "runCmds",
            "params": params,
            "id": id
        }

        resp = self.send("/command-api", data=payload, **kwargs)

        return resp.json()

    def send(self, path, data, **kwargs):
        """Sends the request to EAPI"""


        url = self.prepare_url(path)

        kwargs.setdefault("timeout", self.timeout)

        if self.cert:
            kwargs.setdefault("cert", self.cert)

            if self.verify is not None:
                kwargs.setdefault("verify", self.verify)
        elif not self.logged_in:
            # Note: if the Session key is in cookies no auth parameter is
            # required.
            kwargs.setdefault("auth", self.auth)

        try:
            response = self._session.post(url, data=json.dumps(data), **kwargs)
        except requests.Timeout as exc:
            raise EapiTimeoutError(str(exc))
        except requests.ConnectionError as exc:
            raise EapiError(str(exc))

        return response

# if __name__ == "__main__":
#     import sys
#     from pprint import pprint
#
#     hostaddr = sys.argv[1]
#     cert = sys.argv[2]
#     key = sys.argv[3]
#
#     with Session(hostaddr, protocol="https", cert=(cert, key),
#                  verify=False) as sess:
#         resp = sess.execute(["show version", "show hostname"], format="json")
#         for item in resp.iter_result():
#             pprint(item)
#
#     with Session(hostaddr, protocol="http", auth=("admin", "")) as sess:
#         resp = sess.execute(["show version", "show hostname"], format="json")
#         for item in resp.iter_result():
#             pprint(item)
