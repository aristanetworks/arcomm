# -*- coding: utf-8 -*-

"""High level functional API for using arcomm modules"""

from arcomm.session import Session
from arcomm.util import to_list

def connect(uri, **kwargs):
    sess = Session()
    return sess.connect(uri, **kwargs)

def execute(uri, commands, options):
    with Session() as sess:
        sess.connect(uri, options)

        authorize = options.get('authorize')
        if authorize:
            if hasattr(authorize, '__iter__'):
                username, password = authorize[0], authorize[1]
            else:
                username, password = ('', authorize)
            sess.authorize(password, username)

        return sess.send(commands, options)

send = execute

def configure(uri, commands, options):

    commands = to_list(commands)
    commands.insert(0, "configure")
    commands.append("end")

    execute(uri, commands, options)
