# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import sys

__version_info__ = (2, 2, 2)
__version__ = '2.2.2'

if sys.version_info < (2, 7):
    raise RuntimeError('You need Python 2.7+ for arcomm.')

__title__ = 'arcomm'
__description__ = 'Library for connecting to Arista switches'
__author__ = 'Jesse R. Mather'
__email__ = 'jmather@arista.com'
__uri__ = 'https://github.com/aristanetworks/arcomm'
__license__ = 'MIT License'
__copyright__ = '2016 Arista Networks, Inc.'

from arcomm import util
from arcomm.api import (background, batch, configure, connect, creds, execute,
                        tap)

#
# old v1 funcs
#
from arcomm.api import (authorize, authorized, clone, create_pool, execute_once,
                        execute_pool, execute_bg, execute_until, close,
                        get_credentials)

from arcomm.async import Pool
from arcomm.command import Command, commands_from_list, command_from_dict, mkcmd
from arcomm.credentials import Creds, BasicCreds
from arcomm.session import session, Session
from arcomm.protocols import BaseProtocol
from arcomm.response import (ResponseStore, Response, get_subscribers,
                             subscribe, unsubscribe)
from arcomm.exceptions import (ConnectFailed, AuthenticationFailed,
                               AuthorizationFailed, ExecuteFailed)
