# -*- coding: utf-8 -*-

"""High level functional API for using arcomm modules"""

import re
import time

from arcomm.session import Session
from arcomm.util import to_list
from arcomm.async import Pool
from arcomm.credentials import BasicCreds

def connect(uri, creds=None, **kwargs):
    if creds:
        kwargs['creds'] = creds

    sess = Session()
    sess.connect(uri, **kwargs)
    return sess

def configure(uri, commands,  **kwargs):

    commands = to_list(commands)
    commands.insert(0, "configure")
    commands.append("end")

    execute(uri, commands,  **kwargs)

def execute(uri, commands, **kwargs):

    with Session() as sess:
        sess.connect(uri,  **kwargs)

        authorize = kwargs.get('authorize')
        if authorize:
            if hasattr(authorize, '__iter__'):
                username, password = authorize[0], authorize[1]
            else:
                username, password = ('', authorize)
            sess.authorize(password, username)

        return sess.execute(commands,  **kwargs)

def batch(endpoints, commands, **kwargs):
    endpoints = to_list(endpoints)

    #pool_size = kwargs.pop('pool_size', None) or 10
    delay = kwargs.pop('delay', None) or 0

    pool = Pool(endpoints, commands, **kwargs)
    pool.run(delay=delay)

    for item in pool.results:
        yield item

def background(uri, commands, **kwargs):
    pool = Pool(uri, commands, **kwargs)
    pool.background = True
    return pool

#
# Old functions, backward compatible
#

def authorize(connection, secret=''):
    """Authorize the given connection for elevated privileges"""
    connection.authorize(secret)

def authorized(connection):
    """Return authorization status of connection"""
    return connection.authorized

def clone(connection, uri=None, creds=None, protocol=None, timeout=None,
          **kwargs):

    if creds:
        kwargs['creds'] = creds

    if protocol:
        kwargs['protocol'] = protocol

    if timeout:
        kwargs['timeout'] = timeout

    return connection.clone(uri, **kwargs)

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
    return connection.execute(commands, **kwargs)

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
    pool = async.Pool(hosts, creds=creds, commands=commands, **kwargs)
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
    """Runs a command until a condition has been met or the timeout
    (in seconds) is exceeded. If 'exclude' is set this function will return
    only if the string is _not_ present"""
    #pylint: disable=too-many-arguments
    start_time = time.time()
    check_time = start_time
    response = None
    while (check_time - timeout) < start_time:
        response = connection.execute(commands)
        _match = re.search(re.compile(condition), str(response))
        if exclude:
            if not _match:
                return response
        elif _match:
            return response
        time.sleep(sleep)
        check_time = time.time()
    raise ValueError("condition did not match withing timeout period")

def get_credentials(username, password="", authorize_password=None,
                    private_key=None):
    """Return a Creds object. If username and password are not passed the user
    will be prompted"""
    return BasicCreds(username, password,
                            authorize_password=authorize_password,
                            private_key=private_key)
