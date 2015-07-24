# -*- coding: utf-8 -*-
"""Eapi module to replace need for jsonrpclib"""
import json
import urllib2

class _EapiException(Exception):
    """base class for Eapi errors"""
    pass

class _Eapi(object):
    """Simple implementation of a Eapi client that does not use jsonrpclib"""

    #pylint: disable=too-many-instance-attributes
    __protocol = None
    __uri = None

    def __init__(self, host, username, password="", enable="", use_ssl=False,
                 port=None):
        self.eapi_id = "arcomm.protocols." + self.__class__.__name__
        self.host = host
        self.user = username
        self.password = password
        self.enable_pass = enable or ""
        self.enabled = False
        self.protocol = "http" if not use_ssl else "https"
        self.port = port or (80 if self.protocol == "http" else 443)
        self.http = self._get_auth_opener()

    @property
    def protocol(self):
        #pylint: disable=missing-docstring
        return self.__protocol

    @protocol.setter
    def protocol(self, value):
        #pylint: disable=missing-docstring
        if value not in ("http", "https"):
            raise ValueError("protocol must be 'http' or 'https'")
        self.__protocol = value

    @property
    def uri(self):
        """generate and return the URI"""
        if hasattr(self, "__uri"):
            return self.__uri
        _uri = "{}://{}:{}/command-api"
        self.__uri = _uri.format(self.protocol, self.host, self.port)
        return self.__uri

    def _get_auth_opener(self):
        """create a URL opener with an authentication handler"""
        passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passmgr.add_password(None, self.uri, self.user, self.password)
        handler = urllib2.HTTPBasicAuthHandler(passmgr)
        opener = urllib2.build_opener(handler)
        return opener.open

    def _request(self, commands, timestamps=False, encoding="text"):
        """generate the request data"""

        params = {"version": 1, "cmds": commands, "format": encoding}
        # timestamps is a newer param, only include it if requested
        if timestamps:
            params["timestamps"] = timestamps

        return json.dumps({"jsonrpc": "2.0", "method": "runCmds",
                           "params": params, "id": self.eapi_id})

    def _send(self, data):
        """send the request data to the host and return the response"""

        header = {'Content-Type': 'application/json'}
        req = urllib2.Request(self.uri, data, header)

        try:
            response = self.http(req)
        except urllib2.URLError as exc:
            raise _EapiException("Error: {}".format(exc.reason))

        data = json.loads(response.read())

        return data

    def enable(self):
        """set the session as 'enabled' and prepend the 'enable' command to all
        subsequent calls to `execute`"""

        # test enable...
        response = self.execute([self._enable()])

        if "error" in response:
            raise _EapiException(response["error"]["message"])

        self.enabled = True

    def _enable(self):
        return {"cmd": "enable", "input": self.enable_pass}

    def execute(self, commands, **kwargs):
        """execute a series of commands on a remote host. removes the output
        item for the 'enable' command if `self.enabled` is True"""
        if self.enabled:
            commands = [self._enable()] + commands

        request = self._request(commands, **kwargs)
        response = self._send(request)

        if self.enabled:
            response["result"].pop(0)
        return response
