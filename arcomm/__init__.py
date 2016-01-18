# -*- coding: utf-8 -*-

"""

"""

__description__ = 'Library for connecting to Arista switches'
__version__ = '2.0.0-beta.8'
__author__ = 'Jesse Mather'
__uri__ = 'https://github.com/aristanetworks/arcomm'
__license = 'MIT Licesnse'
# pylint: disable=wildcard-import
from . import util
from .api import background, batch, configure, connect, execute, tap

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
from .protocols import BaseProtocol
from .response import ResponseStore, Response
from .exceptions import (
    ConnectFailed, AuthenticationFailed, AuthorizationFailed, ExecuteFailed
)
