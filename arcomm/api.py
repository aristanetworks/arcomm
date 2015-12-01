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

def get_credentials(username, password="", authorize_password=None,
                    private_key=None):
    """Return a Creds object. If username and password are not passed the user
    will be prompted"""
    return BasicCreds(username, password,
                            authorize_password=authorize_password,
                            private_key=private_key)
