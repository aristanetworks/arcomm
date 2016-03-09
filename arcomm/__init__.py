# -*- coding: utf-8 -*-

"""

"""

import sys

__version_info__ = (2, 0, 7)
__version__ = '2.0.7'

if sys.version_info < (2, 6):
    raise RuntimeError('You need Python 2.6+ for arcomm.')

__title__ = 'arcomm'
__description__ = 'Library for connecting to Arista switches'
__author__ = 'Jesse R. Mather'
__email__ = 'jmather@arista.com'
__uri__ = 'https://github.com/aristanetworks/arcomm'
__license__ = 'MIT License'
__copyright__ = '2016 Arista Networks, Inc.'

from . import util
from .api import background, batch, configure, connect, execute, tap

#
# old v1 funcs
#
from .api import (get_credentials, authorize, authorized, clone, create_pool,
                  execute_once, execute_pool, execute_bg, execute_until, close)
from .async import Pool
#from .cli import Cli
from .command import Command
from .credentials import Creds, BasicCreds
from .session import session, Session
from .protocols import BaseProtocol
from .response import ResponseStore, Response
from .exceptions import (ConnectFailed, AuthenticationFailed,
                         AuthorizationFailed, ExecuteFailed)
