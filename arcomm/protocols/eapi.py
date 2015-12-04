# -*- coding: utf-8 -*-
try:
    import requests_unixsocket
    requests_unixsocket.monkeypatch()
except ImportError:
    pass

import json
import requests
import warnings
from arcomm.exceptions import AuthenticationFailed, ExecuteFailed
# try:
#     import paramiko
# except ImportError:
#     pass

from arcomm.protocols.protocol import BaseProtocol
#from arcomm.protocols._ssh_forward import
from arcomm.command import Command

class BaseTransport(object):

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

    def connect(self, host, creds, port):
        raise NotImplementedError

    def send(self, commands):
        raise NotImplementedError

class HttpTransport(BaseTransport):

    def __init__(self):
        self.scheme = 'http'
        self.endpoint = None
        self.creds = None
        self.headers = {'Content-Type': 'application/json'}

    def get_endpoint(self, host, port=None):
        endpoint = '{}://{}'.format(self.scheme, host)

        if port:
            endpoint += ':{}'.format(port)

        endpoint += '/command-api'

        return endpoint

    def connect(self, host, creds=None, port=None):
        self.endpoint = self.get_endpoint(host, port)
        self.creds = creds

    def send(self, commands, encoding='text', timestamps=False):

        creds = self.creds.auth if hasattr(self.creds, 'auth') else None

        payload = self.payload(commands, encoding, timestamps)
        response = requests.post(self.endpoint, auth=creds,
                                 headers=self.headers, data=json.dumps(payload))

        response.raise_for_status()
        return response

class HttpsTransport(HttpTransport):

    def __init__(self):
        super(HttpsTransport, self).__init__()
        self.scheme = 'https'

class UnixTransport(BaseTransport):

    def __init__(self):
        super(UnixTransport, self).__init__()
        self.scheme = 'http+unix'

# class SshTransport(HttpTransport):
#     pass

def _format_commands(commands):
    """converts commands to Eapi formatted dicts"""

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
            'https': HttpsTransport,
            'unix': UnixTransport,
            #'ssh': SshTransport
        }

    def close(self):
        self._conn = None

    def connect(self, host, creds, **kwargs):

        transport = kwargs.get('transport', None) or 'http'
        port = kwargs.get('port')

        self._conn = self._transports[transport]()
        self._conn.connect(host, creds, port=port)

        try:
            # test the connection
            self.send([Command('')])
        except ExecuteFailed as exc:
            if '401 Client Error' in exc.message:
                raise AuthenticationFailed(exc.message)

    def send(self, commands, **kwargs):

        results = []

        encoding = kwargs.get('encoding', 'text')
        timestamps = kwargs.get('timestamps', False)

        if self._authorize:
            commands = [self._authorize] + commands

        try:
            response = self._conn.send(_format_commands(commands),
                                       encoding=encoding, timestamps=timestamps)
        #     print "RESPONSE:", response
        except (requests.HTTPError, requests.ConnectionError) as exc:
            raise ExecuteFailed(exc.message)

        data = response.json()

        if 'error' in data:
            err_code = data['error']['code']
            err_msg = data['error']['message']
            data = data['error']['data']
            raise ExecuteFailed("[{}] {}".format(err_code, err_msg))

        for item in data['result']:
            if encoding == 'text':
                output = item['output']
            else:
                output = item

            results.append(output)

        if len(results) > 1 and self._authorize:
            results.pop(0)

        return results

    def authorize(self, password, username):
        self._authorize = Command({'cmd': 'enable', 'input': password})
