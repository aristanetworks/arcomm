# -*- coding: utf-8 -*-

"""

"""

__version__ = '2.0.0'
__author__ = 'Jesse Mather'

# pylint: disable=wildcard-import
from . import util
from .api import connect, execute, configure
from .credentials import Creds, BasicCreds
from .session import session, Session
from .response import ResponseStore, Response
from .exceptions import (
    ConnectFailed, AuthenticationFailed, AuthorizationFailed, ExecuteFailed
)
