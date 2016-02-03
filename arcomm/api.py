# -*- coding: utf-8 -*-

"""High level functional API for using arcomm modules"""

import re
import time

from arcomm.session import BaseSession, Session
from arcomm.util import to_list
from arcomm.async import Pool
from arcomm.credentials import BasicCreds

def connect(endpoint, creds=None, protocol=None, **kwargs):
    """Construct a :class:`Session <Session>` and make the connection

    :param endpoint: remote host or URI to connect to
    :param creds: (optional) :class:`Creds <Creds>` object with authentication credentials
    :param protocol: (optional) Protocol name, e.g. 'ssh' or 'eapi'

    Usage:
        >>> import arcomm
        >>> conn = arcomm.connect('ssh://veos', creds=BasicCreds('admin', ''))
    """

    if isinstance(creds, (tuple, list)):
        creds = BasicCreds(*creds)

    sess = Session(endpoint, creds, protocol, **kwargs)
    sess.connect()

    return sess

def configure(endpoint, commands,  **kwargs):
    """Make configuration changes to the switch

    :param endpoint: remote host or URI to connect to
    :param commands: command or commands to send
    :param creds: (optional) :class:`Creds <Creds>` object with authentication credentials
    :param protocol: (optional) Protocol name, e.g. 'ssh' or 'eapi'

    Usage:
        >>> import arcomm
        >>> arcomm.configure('eapi://veos', ['interface Ethernet1', 'no shutdown'])
        <ResponseStore [ok]>
    """
    commands = to_list(commands)
    commands.insert(0, "configure")
    commands.append("end")

    execute(endpoint, commands,  **kwargs)

def execute(endpoint, commands, **kwargs):
    """Send exec commands

    :param endpoint: remote host or URI to connect to
    :param commands: command or commands to send
    :param creds: (optional) :class:`Creds <Creds>` object with authentication credentials
    :param protocol: (optional) Protocol name, e.g. 'ssh' or 'eapi'

    Usage:
        >>> import arcomm
        >>> arcomm.configure('eapi://veos', ['show version'])
        <ResponseStore [ok]>
    """
    authorize = kwargs.pop('authorize', None)

    # allow an existing session to be used
    if not isinstance(endpoint, BaseSession):
        sess = Session(endpoint, **kwargs)
        sess.connect()
    else:
        sess = endpoint


    if authorize:
        if hasattr(authorize, '__iter__'):
            username, password = authorize[0], authorize[1]
        else:
            username, password = ('', authorize)
        sess.authorize(password, username)

    response = sess.send(commands,  **kwargs)

    return response

def batch(endpoints, commands, **kwargs):
    endpoints = to_list(endpoints)

    #pool_size = kwargs.pop('pool_size', None) or 10
    delay = kwargs.pop('delay', None) or 0

    pool = Pool(endpoints, commands, **kwargs)
    pool.run(delay=delay)

    for item in pool.results:
        yield item

def background(endpoint, commands, **kwargs):
    pool = Pool([endpoint], commands, **kwargs)
    pool.background = True
    return pool

def tap(callback, func, *args, **kwargs):
    result = func(*args, **kwargs)
    callback(result)
    return result

#
# Old functions, backward compatible
#

def authorize(connection, secret=''):
    """Authorize the given connection for elevated privileges"""
    connection.authorize(secret)

def authorized(connection):
    """Return authorization status of connection"""
    return connection.authorized

def clone(connection, endpoint=None, creds=None, protocol=None, timeout=None,
          **kwargs):

    if timeout:
        kwargs['timeout'] = timeout

    return connection.clone(endpoint, **kwargs)

def monitor(connection, func):
    pass

def close(connection):
    """Close the connection"""
    connection.close()

def configure(connection, commands, *args, **kwargs):
    """Similar to execute, but wraps the commands in a configure/end block"""
    commands = to_list(commands)
    commands.insert(0, "configure")
    commands.append("end")
    return connection.send(commands, **kwargs)

def connect_with_password(host, username, password="", **kwargs):
    """Use a username and password to connect to host"""
    creds = arcomm.BasicCreds(username, password)
    return connect(host, creds=creds, **kwargs)

connect_uri = connect

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
        print result
    """
    pool = Pool(hosts, creds=creds, commands=commands, **kwargs)
    return pool

def execute_bg(host, creds, commands, **kwargs):
    kwargs['creds'] = creds
    return background(host, commands, **kwargs)

def execute_once(host, creds, commands, **kwargs):
    kwargs['creds'] = creds
    return execute(host, commands, **kwargs)

def execute_pool(hosts, creds, commands, **kwargs):
    kwargs['creds'] = creds
    return batch(hosts, commands, **kwargs)

def execute_until(connection, commands, condition, timeout=30, sleep=5,
                  exclude=False):
    return connection.execute_until(commands, condition, timeout=timeout,
                                    sleep=sleep, exclude=exclude)

def get_credentials(username, password="", authorize_password=None,
                    private_key=None):
    """Return a Creds object. If username and password are not passed the user
    will be prompted"""
    return BasicCreds(username, password,
                            authorize_password=authorize_password,
                            private_key=private_key)
