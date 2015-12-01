# -*- coding: utf-8 -*-

"""High level functional API for using arcomm modules"""

from arcomm.session import Session
from arcomm.util import to_list
from arcomm.async import Pool

def connect(uri, **kwargs):
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

# def execute_until(connection, commands, condition, timeout=30, sleep=5,
#                   exclude=False):
#     """Runs a command until a condition has been met or the timeout
#     (in seconds) is exceeded. If 'exclude' is set this function will return
#     only if the string is _not_ present"""
#     #pylint: disable=too-many-arguments
#     start_time = time.time()
#     check_time = start_time
#     response = None
#     while (check_time - timeout) < start_time:
#         response = execute(connection, commands)
#         _match = re.search(re.compile(condition), str(response))
#         if exclude:
#             if not _match:
#                 return response
#         elif _match:
#             return response
#         time.sleep(sleep)
#         check_time = time.time()
#     raise ValueError("condition did not match withing timeout period")
