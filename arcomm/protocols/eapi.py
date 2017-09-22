# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

try:
    import requests_unixsocket
    requests_unixsocket.monkeypatch()
except ImportError:
    pass

import abc
import json
import requests
import warnings

from arcomm.exceptions import AuthenticationFailed, ConnectFailed, ExecuteFailed
from arcomm.protocols.protocol import BaseProtocol
from arcomm.util import zipnpad
from arcomm.command import Command
from arcomm.response import Response
from requests.packages.urllib3.exceptions import InsecureRequestWarning

class BaseTransport(object):
    __metaclass__  = abc.ABCMeta

    def payload(self, commands, encoding, timestamps=False):
        """generate the request data"""
        id =  'arcomm-' + self.__class__.__name__
        params = {
            'version': 1,
            'cmds': commands,
            'format': encoding
        }
        # timestamps is a newer param, only include it if requested
        if timestamps:
            params['timestamps'] = timestamps

        return {
            'jsonrpc': '2.0',
            'method': 'runCmds',
            'params': params,
            'id': id
        }

    @abc.abstractmethod
    def send(self, commands, encoding, timestamps, timeout):
        pass

class HttpTransport(BaseTransport):

    def __init__(self, host, creds=None, port=None, timeout=None):
        self.scheme = 'http'
        self.host = host
        self.creds = creds
        self.port = port
        self.timeout = timeout
        self.headers = {'Content-Type': 'application/json'}

    def get_endpoint(self):
        endpoint = '{}://{}'.format(self.scheme, self.host)

        if self.port:
            endpoint += ':{}'.format(self.port)

        endpoint += '/command-api'

        return endpoint

    def send(self, commands, encoding='text', timestamps=False, timeout=None):
        endpoint = self.get_endpoint()

        creds = self.creds.auth if hasattr(self.creds, 'auth') else None

        if not timeout:
            timeout = self.timeout

        payload = self.payload(commands, encoding, timestamps)


        response = requests.post(endpoint, auth=creds,
                                 headers=self.headers,
                                 data=json.dumps(payload),
                                 verify=False,
                                 timeout=timeout)

        response.raise_for_status()
        return response

class HttpsTransport(HttpTransport):

    def __init__(self, *args, **kwargs):
        super(HttpsTransport, self).__init__(*args, **kwargs)
        self.scheme = 'https'

    def send(self, commands, encoding='text', timestamps=False, timeout=None):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=InsecureRequestWarning)

            return super(HttpsTransport, self).send(commands, encoding,
                                                    timestamps, timeout)

def _format_commands(commands):
    """converts commands to Eapi formatted dicts"""
    #print(commands)
    formatted = []
    for command in commands:
        answer = command.answer or ''
        command = command.cmd.strip()
        formatted.append({'cmd': command, 'input': answer})

    return formatted

class Eapi(BaseProtocol):

    def __init__(self):
        self._authorize = None
        self._conn = None

        self._transports = {
            'http': HttpTransport,
            'https': HttpsTransport
        }

    def close(self):
        self._conn = None

    def connect(self, host, creds, **kwargs):

        transport = kwargs.get('transport', None) or 'http'

        port = kwargs.get('port')

        timeout = kwargs.get('timeout', None)

        self._conn = self._transports[transport](host, creds, port=port,
                                                 timeout=timeout)

        try:
            # test the connection
            self.send([Command('show hostname')])
        except ExecuteFailed as exc:
            if '401 Client Error' in str(exc):
                raise AuthenticationFailed(str(exc))
            else:
                raise ConnectFailed(str(exc))

    def send(self, commands, **kwargs):

        encoding = kwargs.get('encoding', 'text')
        timestamps = kwargs.get('timestamps', False)
        timeout = kwargs.get('timeout', None)

        results = []
        status_code = 0
        status_message = None
        result = None

        if self._authorize:
            commands = [self._authorize] + commands

        try:
            response = self._conn.send(_format_commands(commands),
                                       encoding=encoding,
                                       timestamps=timestamps,
                                       timeout=timeout)

        except (requests.HTTPError,
                requests.ConnectionError,
                requests.Timeout) as exc:
            raise ExecuteFailed(str(exc))

        data = response.json()

        if 'error' in data:
            status_code = data['error']['code']
            status_message = data['error']['message']
            result = data['error']['data']
        else:
            result = data['result']

        for command, result in zipnpad(commands, result):
            errored = None
            output = None

            if result:
                if encoding == 'text':
                    output = result['output']
                else:
                    output = result

                if 'errors' in result:
                    errored = True
                else:
                    errored = False

            results.append([command, output, errored])

        if len(results) > 1 and self._authorize:
            results.pop(0)

        return (results, status_code, status_message)

    def authorize(self, password, username):
        self._authorize = Command({'cmd': 'enable', 'input': password})
