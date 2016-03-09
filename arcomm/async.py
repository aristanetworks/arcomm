# -*- coding: utf-8 -*-
"""

"""

import multiprocessing
import time
import signal
import sys
import traceback

from arcomm.session import Session
from arcomm.exceptions import (ExecuteFailed, ConnectFailed,
                               AuthenticationFailed, AuthorizationFailed)
from arcomm.response import ResponseStore, Response
from arcomm.util import to_list



def _prep_worker():
    """Tell workers to ignore interrupts"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def _worker(host, commands, **kwargs):
    """Common worker func. Logs into remote host, executes commands and puts
    the results in the queue. Called from `Pool` and `Background`"""

    responses = None
    try:
        with Session(host, **kwargs) as sess:

            authorize = kwargs.pop('authorize', None)

            if authorize:
                sess.authorize(authorize)

            responses = sess.execute(commands, **kwargs)

    except (ConnectFailed,
            AuthenticationFailed,
            AuthorizationFailed) as exc:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        repr_ = "\n".join(traceback.format_exception(exc_type, exc_value,
                         exc_traceback))

        # if we get kicked out of the session... we have to make our own
        # response object... :(
        responses = ResponseStore(host, **kwargs)
        responses.append(Response('_authentication', repr_, errored=True))

    return responses

class Pool(object):
    """
    """

    def __init__(self, endpoints, commands, size=10, delay=0, **kwargs):

        #
        self._endpoints = to_list(endpoints)

        #
        self._commands = commands

        #
        self._pool_size = size

        #
        #self.background = kwargs.pop('background', False)
        self._delay = delay

        #
        self._worker_kwargs = kwargs

        #
        self._results = []

        # initialize pool
        self._pool = multiprocessing.Pool(self._pool_size, _prep_worker)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        #self.join()
        pass

    def __iter__(self):
        for item in self._results:
            yield item.get()

    @property
    def results(self):
        """Returns the results queue"""
        return self._results

    def run(self, **kwargs):
        """Run commands on the hosts, blocks until are tasks are completed"""
        self.start(**kwargs)
        self.join()

    def start(self): #, delay=0, background=False, sleep=0):
        """Run through host is the pool aysnchronously.  If sleep is > 0, start
        will wait for specified noumber of seconds before returning."""

        for host in self._endpoints:
            args = [host, self._commands]
            result = self._pool.apply_async(_worker, args, self._worker_kwargs)
            self._results.append(result)

        self._pool.close()

        time.sleep(self._delay)

    def join(self):
        self._pool.join()

    def kill(self):
        """Terminate the pool and empty the queue"""

        self._pool.terminate()
