# -*- coding: utf-8 -*-

"""High level functional API for using arcomm modules"""

from arcomm.session import Session
from arcomm.util import to_list

def connect(uri, **kwargs):
    sess = Session()
    return sess.connect(uri, **kwargs)

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
