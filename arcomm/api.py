# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""High level functional API for using arcomm modules"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import re
import sys
import time

from arcomm.session import BaseSession, Session
from arcomm.util import to_list
from arcomm.async import Pool
from arcomm.credentials import BasicCreds, mkcreds
from arcomm.command import Command

import warnings

__all__ = ['authorize', 'authorized', 'background', 'batch', 'clone', 'close',
           'configure', 'connect',  'creds', 'execute', 'execute_until',
           'get_credentials', 'tap']

def authorize(connection, secret=''):
    """Authorize the given connection for elevated privileges"""
    connection.authorize(secret)

def authorized(connection):
    """Return authorization status of connection"""
    return connection.authorized

def background(endpoints, commands, **kwargs):
    """Similar to batch, but the :class:`Pool` opject is returned before
    reading the results, non-blocking

    :param endpoint: remote host or URI to connect to
    :param commands: command or commands to send
    :param creds: (optional) :class:`Creds <Creds>` object with authentication
                             credentials
    :param protocol: (optional) Protocol name, e.g. 'ssh' or 'eapi'
    :return: :class:`Pool <Pool>` object
    :rtype: arcomm.async.Pool

    Usage:
        >>> with arcomm.background('veos1', 'show version') as bg:
        ...     # do other things...
        ...
        >>> for res in bg:
        ...     print(res.to_yaml())
        ...
        host: vswitch1
        status: ok
        commands:
          - command: show version
            output: |
              Arista vEOS
              Hardware version:
              Serial number:
              System MAC address:  0800.2776.48c5
              [ ...output omitted... ]
    """

    endpoints = to_list(endpoints)
    return Pool(endpoints, commands, **kwargs)

def batch(endpoints, commands, **kwargs):
    """Send commands to multiple endpoints

    :param endpoint: remote host or URI to connect to
    :param commands: command or commands to send
    :param creds: (optional) :class:`Creds <Creds>` object with authentication
                             credentials
    :param protocol: (optional) Protocol name, e.g. 'ssh' or 'eapi'

    Usage:
        >>> pool = arcomm.batch(['veos1', 'veos2'], ['show version'])
        >>> for res in pool:
        ...     print(res.to_yaml())
    """

    endpoints = to_list(endpoints)
    with Pool(endpoints, commands, **kwargs) as pool:
        try:
            for item in pool.results:
                yield item.get()
        except KeyboardInterrupt:
            print('Caught interrupt')
            pool.kill()
            raise

def configure(endpoint, commands,  **kwargs):
    """Make configuration changes to the switch

    :param endpoint: remote host or URI to connect to
    :param commands: configuration mode command or commands to send
    :param creds: (optional) :class:`Creds <Creds>` object with authentication
                             credentials
    :param protocol: (optional) Protocol name, e.g. 'ssh' or 'eapi'

    Usage:
        >>> arcomm.configure('eapi://veos',
        ...                  ['interface Ethernet1', 'no shutdown'])
        <ResponseStore [ok]>
    """
    commands = to_list(commands)
    commands.insert(0, "configure")
    commands.append("end")

    execute(endpoint, commands,  **kwargs)

def connect(endpoint, creds=None, protocol=None, **kwargs):
    """Construct a :class:`Session <Session>` and make the connection

    :param endpoint: remote host or URI to connect to
    :param creds: (optional) :class:`Creds <Creds>` object with authentication
                             credentials
    :param protocol: (optional) Protocol name, e.g. 'ssh' or 'eapi'

    Usage:
        >>> import arcomm
        >>> conn = arcomm.connect('ssh://veos', creds=BasicCreds('admin', ''))
    """
    if isinstance(creds, (tuple, list)):
        creds = BasicCreds(*creds)

    sess = Session(endpoint, creds=creds, protocol=protocol, **kwargs)
    sess.connect()

    return sess

def creds(username, password="", **kwargs):
    """Return a Creds object. If username and password are not passed the user
    will be prompted"""

    return mkcreds(username, password=password, **kwargs)
# old name
get_credentials = creds

def execute(endpoint, commands, creds=("admin", ""), protocol=None,
            authorize=None, **kwargs):
    """Send exec commands

    :param authorize: enter enable mode
    :param endpoint: remote host or URI to connect to
    :param commands: command or commands to send
    :param creds: (optional) :class:`Creds <Creds>` object with authentication
                             credentials
    :param protocol: (optional) Protocol name, e.g. 'ssh' or 'eapi'

    Usage:
        >>> arcomm.configure('eapi://veos', ['show version'])
        <ResponseStore [ok]>
    """

    # allow an existing session to be used
    if not isinstance(endpoint, BaseSession):
        sess = Session(endpoint, creds=creds, protocol=protocol, **kwargs)
        sess.connect()
    else:
        sess = endpoint

    if authorize is not None:
        sess.authorize(authorize, None)

    response = sess.send(commands,  **kwargs)

    return response

send = execute

def tap(callback, func, *args, **kwargs):
    """What does this even accomplish..."""
    result = func(*args, **kwargs)
    callback(result)
    return result

def clone(connection, endpoint=None, **kwargs):

    return connection.clone(endpoint, **kwargs)

# def monitor(connection, func):
#     pass

def close(connection):
    """Close the connection"""
    connection.close()

def configure(connection, commands, *args, **kwargs):
    """Similar to execute, but wraps the commands in a configure/end block"""
    commands = to_list(commands)
    commands.insert(0, "configure")
    commands.append("end")
    return connection.send(commands, **kwargs)

def execute_until(connection, commands, condition, timeout=30, sleep=5,
                  exclude=False):
    return connection.execute_until(commands, condition, timeout=timeout,
                                    sleep=sleep, exclude=exclude)

#
# Old functions, backward compatible
#
connect_uri = connect

def connect_with_password(host, username, password="", **kwargs):
    """Use a username and password to connect to host"""
    creds = arcomm.BasicCreds(username, password)
    return connect(host, creds=creds, **kwargs)

def create_uri(host, protocol, username, password, port):
    """Create a URI from given parts"""
    creds = get_credentials(username=username, password=password)
    credspart = "{}:{}".format(creds.username, creds.password)
    portpart = ":{}".format(port) if port else ""
    uri = "{}://{}@{}{}".format(protocol, credspart, host, portpart)
    return uri

def create_pool(hosts, creds, commands, **kwargs):
    """Return a `Pool` object of hosts and commands

    Example:
    pool = create_pool(["spine1a", "spine2a"], creds, "show version")
    pool.start()
    # do other stuff...
    pool.join()
    for result in pool.results:
        print(result)
    """
    warnings.warn("deprecated", DeprecationWarning)
    pool = Pool(hosts, creds=creds, commands=commands, **kwargs)
    return pool

def execute_bg(host, creds, commands, **kwargs):
    warnings.warn("deprecated", DeprecationWarning)
    kwargs['creds'] = creds
    return background(host, commands, **kwargs)

def execute_once(host, creds, commands, **kwargs):
    warnings.warn("deprecated", DeprecationWarning)
    kwargs['creds'] = creds
    return execute(host, commands, **kwargs)

def execute_pool(hosts, creds, commands, **kwargs):
    warnings.warn("deprecated", DeprecationWarning)
    kwargs['creds'] = creds
    return batch(hosts, commands, **kwargs)
