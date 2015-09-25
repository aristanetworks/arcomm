# -*- coding: utf-8 -*-
"""Eapi adpter"""
from ._eapi import _Eapi, _EapiException
from ..protocol import Protocol
from ..exceptions import ConnectFailed, ExecuteFailed, AuthorizationFailed

def _format_commands(commands):
    """converts commands to Eapi formatted dicts"""
    formatted = []
    for command in commands:
        _cmd = str(command).strip()
        _answer = command.answer or ""
        formatted.append(dict(cmd=_cmd, input=_answer))
    return formatted

class Eapi(Protocol):
    """Wrapper class for JSON-RPC API"""
    _marker = ">"
    _use_ssl = False
    _port = 80
    def _on_initialize(self, **kwargs):
        """Setup protocol specific attributes"""
        pass

    def _authorize(self, secret):
        """Authorize the 'session'"""
        try:
            self.connection.enable()
        except _EapiException as exc:
            raise AuthorizationFailed(exc.message)
        self._marker = "#"

    def _connect(self, host, creds):
        """returns a _Eapi object, no connection is made at this time"""
        conn = _Eapi(host, username=creds.username, password=creds.password,
                     enable=creds.authorize_password, use_ssl=self._use_ssl,
                     port=self._port)

        # test the connection
        try:
            conn.execute("show clock")
        except _EapiException as exc:
            raise ConnectFailed(str(exc))

        return conn

    def _sendall(self, commands, encoding="text", timestamps=False):
        """Send all commands in one request. Eapi track conext (enabled? or
        configured?, etc...)

        JSON OK:

        {u'id': u'arcomm.protocols._Eapi',
         u'jsonrpc': u'2.0',
         u'result': [{u'architecture': u'i386',
                      u'bootupTimestamp': 1432852261.69,
                      u'hardwareRevision': u'',
                      u'internalBuildId': u'1d97861d-09c7-4fc3-b38d-a98c99b77ae9',
                      u'internalVersion': u'4.15.0F-2387143.4150F',
                      u'memFree': 118540,
                      u'memTotal': 2027964,
                      u'modelName': u'vEOS',
                      u'serialNumber': u'',
                      u'systemMacAddress': u'00:0c:29:44:28:8b',
                      u'version': u'4.15.0F'}]}

        TEXT OK:

        {u'id': u'arcomm.protocols._Eapi',
         u'jsonrpc': u'2.0',
         u'result': [{u'output': u'Arista vEOS\nHardware version:    \nSerial number:       \nSystem MAC address:  000c.2944.288b\n\nSoftware image version: 4.15.0F\nArchitecture:           i386\nInternal build version: 4.15.0F-2387143.4150F\nInternal build ID:      1d97861d-09c7-4fc3-b38d-a98c99b77ae9\n\nUptime:                 15 hours and 11 minutes\nTotal memory:           2027964 kB\nFree memory:            118656 kB\n\n'}]}

        JSON ERROR:

        {u'error': {u'code': 1002,
                    u'data': [{u'architecture': u'i386',
                               u'bootupTimestamp': 1432852261.69,
                               u'hardwareRevision': u'',
                               u'internalBuildId': u'1d97861d-09c7-4fc3-b38d-a98c99b77ae9',
                               u'internalVersion': u'4.15.0F-2387143.4150F',
                               u'memFree': 118724,
                               u'memTotal': 2027964,
                               u'modelName': u'vEOS',
                               u'serialNumber': u'',
                               u'systemMacAddress': u'00:0c:29:44:28:8b',
                               u'version': u'4.15.0F'},
                              {u'errors': [u"Invalid input (at token 1: 'bogus')"]}],
                    u'message': u"CLI command 2 of 2 'show bogus command' failed: invalid command"},
         u'id': u'arcomm.protocols._Eapi',
         u'jsonrpc': u'2.0'}


        TEXT ERROR:

        {u'error': {u'code': 1002,
                    u'data': [{u'output': u'Arista vEOS\nHardware version:    \nSerial number:       \nSystem MAC address:  000c.2944.288b\n\nSoftware image version: 4.15.0F\nArchitecture:           i386\nInternal build version: 4.15.0F-2387143.4150F\nInternal build ID:      1d97861d-09c7-4fc3-b38d-a98c99b77ae9\n\nUptime:                 15 hours and 10 minutes\nTotal memory:           2027964 kB\nFree memory:            118492 kB\n\n'},
                              {u'errors': [u"Invalid input (at token 1: 'bogus')"],
                               u'output': u"% Invalid input (at token 1: 'bogus')\n"}],
                    u'message': u"CLI command 2 of 2 'show bogus command' failed: invalid command"},
         u'id': u'arcomm.protocols._Eapi',
         u'jsonrpc': u'2.0'}


        SHOULD RETURN

        [({u'architecture': u'i386',
           u'bootupTimestamp': 1432852261.68,
           u'hardwareRevision': u'',
           u'internalBuildId': u'1d97861d-09c7-4fc3-b38d-a98c99b77ae9',
           u'internalVersion': u'4.15.0F-2387143.4150F',
           u'memFree': 78680,
           u'memTotal': 2027964,
           u'modelName': u'vEOS',
           u'serialNumber': u'',
           u'systemMacAddress': u'00:0c:29:44:28:8b',
           u'version': u'4.15.0F'},
          None),
         (None, '% Invalid input')]

        """
        responses = []
        errmsg = None
        commands = _format_commands(commands)

        try:
            response = self.connection.execute(commands, encoding=encoding, timestamps=timestamps)
        except _EapiException as exc:
            raise ExecuteFailed("Send failed: {}".format(exc.message))
        #from pprint import pprint as pp
        if "error" in response:
            data = response["error"]["data"]
            errmsg = "[{}]: {}".format(response["error"]["code"], response["error"]["message"])
            errored = ",".join(data.pop()["errors"])
            data.append({"output": errored})
        else:
            data = response["result"]

        for item in data:
            if "output" in item:
                responses.append((item["output"], None))
            else:
                responses.append((item, None))

        if errmsg:
            response, _ = responses.pop()
            responses.append((response, errmsg))

        return responses
