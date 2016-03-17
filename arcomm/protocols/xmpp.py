# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

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
