# -*- coding: utf-8 -*-
"""

"""

import multiprocessing
import time
import signal
import socket
import sys
import traceback
import logging

import arcomm
from arcomm.session import Session
from arcomm.exceptions import ExecuteFailed, ConnectFailed, \
                              AuthenticationFailed, AuthorizationFailed
from arcomm.util import to_list
# logger = multiprocessing.log_to_stderr()
# logger.setLevel(logging.INFO)

class QueueError(Exception):
    """Queue has gone away or been deleted"""

def _initialize_worker():
    """Tell workers to ignore interrupts"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def _worker(host, commands, outq, **kwargs):
    """Common worker func. Logs into remote host, executes commands and puts
    the results in the queue. Called from `Pool` and `Background`"""

    responses = None

    with Session() as sess:
        try:
            sess.connect(host, **kwargs)

            authorize = kwargs.pop('authorize', None)

            if authorize:
                sess.authorize(authorize)

            responses = sess.execute(commands, **kwargs)

            sess.close()

        except (ConnectFailed,
                AuthenticationFailed,
                AuthorizationFailed) as exc:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            responses = repr(traceback.format_exception(exc_type, exc_value,
                                            exc_traceback))

    outq.put(responses)

class Pool(object):
    """

    """

    def __init__(self, hosts, commands, **kwargs):

        #
        self._hosts = to_list(hosts)

        #
        self._commands = commands

        #
        self._pool_size = kwargs.pop('pool_size', None) or 10

        #
        self._worker_kwargs = kwargs

        #
        self._results = IterQueue()

        #
        self.background = False

        #
        #self._async_result = None

        # initialize pool
        self._pool = multiprocessing.Pool(self._pool_size, _initialize_worker)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.join()

    @property
    def results(self):
        """Returns the results queue"""
        return self._results

    def run(self, **kwargs):
        """Run commands on the hosts"""
        self.start(**kwargs)
        self.join()

    def start(self, delay=0, background=False):
        """Run through host is the pool aysnchronously.  If sleep is > 0, start
        will wait for specified noumber of seconds before returning."""

        try:
            for host in self._hosts:
                args = [host, self._commands, self.results]
                res = self._pool.apply_async(_worker, args, self._worker_kwargs)

                if not (self.background or background):
                    res.get(2**32)

            self._pool.close()

        except KeyboardInterrupt:

            self.kill()
            raise

        time.sleep(delay)

    def join(self):
        """Bring the pool into the current process (Blocking) and wait for jobs
        to complte.  Also, close the results queue before returning"""
        self._pool.join()
        self._finish()

    def kill(self):
        """Terminate the pool and empty the queue"""
        self._pool.terminate()
        self._results = IterQueue()
        self._finish()

    def _finish(self):
        self._results.close()

class IterQueue(object):
    """Simple queue that can be passed between processes"""
    _sentinel = "__STOP__"

    def __init__(self):
        # pylint: disable=E1101
        _manager = multiprocessing.Manager()
        self._queue = _manager.Queue()
        self._closed = False

    @property
    def closed(self):
        """return True if queue is closed"""
        return self._closed

    def __iter__(self):
        return iter(self._queue.get, self._sentinel)

    def close(self):
        """Shut down the queue and append the sentinel"""
        try:
            self._queue.put(self._sentinel)
        except socket.error as err:
            raise QueueError("{}".format(err))
        self._closed = True

    def get(self, block=True, timeout=None):
        """Pop an item from the queue"""
        return self._queue.get(block, timeout)

    def put(self, item, block=True, timeout=None):
        """Append and item onto the queue"""
        return self._queue.put(item, block, timeout)
