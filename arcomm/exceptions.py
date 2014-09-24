# -*- coding: utf-8 -*-
# Copyright (c) 2014 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
"""
exceptions for arcomm modules
"""
class ProtocolError(Exception):
    """Don't use me"""

class ProtocolException(ProtocolError):
    """Base exception for protocols"""

class ProtocolExecutionError(ProtocolException):
    """OLD: Raised if there is an error while executing commands"""

class ConnectFailed(ProtocolException):
    """Raised when connection fails"""

class AuthenticationFailed(ProtocolException):
    """Raised when authentication fails"""

class AuthorizationFailed(ProtocolException):
    """Raised when authorization fails"""

class ExecuteFailed(ProtocolException):
    """Raised for execution failures"""

class Timeout(ProtocolException):
    """Timed out while waiting for response"""

class QueueError(Exception):
    "Queue has gone away or been deleted"

