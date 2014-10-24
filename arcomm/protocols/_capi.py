# -*- coding: utf-8 -*-
"""CAPI module to replace need for jsonrpclib"""
import json
import urllib2

class _CapiException(Exception):
    pass

class _Capi(object):
    """Simple implementation of a CAPI client that does not use jsonrpclib"""

    #pylint: disable=too-many-instance-attributes
    __enable = __encoding = __protocol = __timestamps = __uri = None

    def __init__(self, host, username, password="", enable="", use_ssl=False,
                 port=None, encoding="json", timestamps=False):
        #pylint: disable=too-many-arguments
        self.capi_id = "arcomm.protocols." + self.__class__.__name__
        self.host = host
        self.user = username
        self.password = password
        self.enable_pass = enable
        self.encoding = encoding
        self.timestamps = timestamps
        self.protocol = "http" if not use_ssl else "https"
        self.port = port or (80 if self.protocol == "http" else 443)
        self.http = self._get_auth_opener()

    @property
    def encoding(self):
        #pylint: disable=missing-docstring
        return self.__encoding

    @encoding.setter
    def encoding(self, value):
        #pylint: disable=missing-docstring
        if value not in ("text", "json"):
            raise ValueError("encoding must be 'text' or 'json'")
        self.__encoding = value

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
    def timestamps(self):
        #pylint: disable=missing-docstring
        return self.__timestamps

    @timestamps.setter
    def timestamps(self, value):
        #pylint: disable=missing-docstring
        self.__timestamps = True if value else False

    @property
    def uri(self):
        """generate and return the URI"""
        if hasattr(self, "__uri"):
            return self.__uri
        _uri = "{}://{}:{}/command-api"
        self.__uri = _uri.format(self.protocol, self.host, self.port)
        return self.__uri

    def _check_response(self, response):
        if "error" in response:
            _message = response["error"]["message"]
            _code = response["error"]["code"]
            raise _CapiException("Error [{}]: {}".format(_code, _message))

    def _get_auth_opener(self):
        """create a URL opener with an authentication handler"""
        passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passmgr.add_password(None, self.uri, self.user, self.password)
        handler = urllib2.HTTPBasicAuthHandler(passmgr)
        opener = urllib2.build_opener(handler)
        return opener.open

    def _request(self, commands, timestamps=None, encoding=None):
        """generate the request data"""
        
        if not encoding:
            encoding = self.encoding
        
        if not timestamps:
            timestamps = self.timestamps
        
        params = {"version": 1, "cmds": commands, "format": encoding}
        # timestamps is a newer param, only include it if requested
        if timestamps:
            params["timestamps"] = timestamps

        return json.dumps({"jsonrpc": "2.0", "method": "runCmds",
                           "params": params, "id": self.capi_id})

    def _send(self, data):
        """sned the request data to the host and return the response"""
        header = {'Content-Type': 'application/json'}
        req = urllib2.Request(self.uri, data, header)
        response = self.http(req)
        data = json.loads(response.read())
        self._check_response(data)
        return data
    
    def enable(self):
        self.__enable = True
    
    def execute(self, commands, **kwargs):
        """execute a series of commands on a remote host"""
        
        pop_enable_result = False
        if self.__enable:
            # don't overwrite commands
            commands = list(commands)
            commands.insert(0, {"cmd": "enable", "input": self.enable_pass})
            pop_enable_result = True

        _request = self._request(commands, **kwargs)
        response = self._send(_request)

        if pop_enable_result:
            response["result"].pop(0)
        return response

