# -*- coding: utf-8 -*-

"""

"""

__version__ = '2.0.0-beta.2'
__author__ = 'Jesse Mather'

# pylint: disable=wildcard-import
from . import util
from .api import connect, execute, configure, background, batch

#
# old v1 funcs
#
from .api import get_credentials, authorize, authorized, clone, configure, \
                 create_pool, execute_once, execute_pool, execute_bg, \
                 execute_until, close

from .async import Pool, IterQueue
#from .cli import Cli
from .credentials import Creds, BasicCreds
from .session import session, Session
from .response import ResponseStore, Response
from .exceptions import (
    ConnectFailed, AuthenticationFailed, AuthorizationFailed, ExecuteFailed
)
