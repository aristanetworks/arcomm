# -*- coding: utf-8 -*-

from arcomm.protocols.protocol import BaseProtocol

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

class Xmpp(BaseProtocol):

    def close(self):
        pass

    def connect(self, host, creds, **kwargs):
        pass

    def send(self, commands, **kwargs):
        pass

    def authorize(self, password, username):
        pass
