# -*- coding: utf-8 -*-
"""exceptions for arcomm modules"""

class ProtocolException(Exception):
    """Base exception for protocols"""

class ConnectFailed(ProtocolException):
    """Raised when connection fails"""

class AuthenticationFailed(ProtocolException):
    """Raised when authentication fails"""

class AuthorizationFailed(ProtocolException):
    """Raised when authorization fails"""

class ExecuteFailed(ProtocolException):
    """Raised for execution failures"""
