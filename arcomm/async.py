# -*- coding: utf-8 -*-
"""Module for handling async communications"""

import arcomm.protocol
from arcomm.exceptions import ConnectFailed, AuthenticationFailed, \
                              AuthorizationFailed, ExecuteFailed
import multiprocessing
import time
import signal
import socket

def _worker_init():
    """Tell workers to ignore interrupts"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

# pylint: disable=R0913
def _worker(host, creds, commands, results, protocol=None, timeout=None,
            encoding="text"):
    """Common worker func. Logs into remote host, executes commands and puts
    the results in the queue. Called from `Pool` and `Background`"""
    response = None
    errmsg = None

    try:
        conn = arcomm.protocol.factory_connect(host, creds, protocol, timeout)
        if creds.authorize_password is not None:
            conn.authorize()
        response = conn.execute(commands, encoding=encoding)
    except (ConnectFailed, AuthenticationFailed, AuthorizationFailed) as exc:
        errmsg = exc.message

    conn.close()
    results.put(dict(host=host, response=response, error=errmsg))

class QueueError(Exception):
    """Queue has gone away or been deleted"""

class Pool(object):
    """Convenience wrapper for Pool.  Send commands to a list of hosts using
    arcomm.execute"""
    def __init__(self, hosts, creds, commands, pool_size=10, **kwargs):
        self._hosts = hosts
        self._creds = creds
        self._commands = commands
        self._pool_size = pool_size
        self._worker_kwargs = kwargs
        self._results = Queue()
        self._async_result = None
        self._pool = multiprocessing.Pool(self._pool_size, _worker_init)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.join()

    @property
    def results(self):
        """Returns the results queue"""
        return self._results

    def run(self):
        """Run commands on the hosts"""
        self.start()
        self.join()

    def start(self, sleep=0):
        """Run through host is the pool aysnchronously.  If sleep is > 0, start
        will wait for specified noumber of seconds before returning."""
        try:
            for host in self._hosts:
                args = [host, self._creds, self._commands, self.results]
                self._async_result = self._pool.apply_async(_worker, args,
                                                            self._worker_kwargs)
                self._async_result.get(2**32)
            self._pool.close()
        except KeyboardInterrupt:
            self.kill()
            raise

        time.sleep(sleep)

    def join(self):
        """Bring the pool into the current process (Blocking) and wait for jobs
        to complte.  Also, close the results queue before returning"""
        self._pool.join()
        self._finish()

    def kill(self):
        """Terminate the pool and empty the queue"""
        self._pool.terminate()
        self._results = Queue()
        self._finish()
    
    def _finish(self):
        self._results.close()
        #self._async_result.get()

class Queue(object):
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
