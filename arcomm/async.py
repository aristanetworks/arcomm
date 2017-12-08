import multiprocessing as mp
import arcomm
import signal
import sys
import time
import traceback

def _prep_worker():
    """Tell workers to ignore interrupts"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def _worker(endpoint, commands, **kwargs):

    try:
        responses = arcomm.execute(endpoint, commands, **kwargs)
    except (arcomm.AuthenticationFailed, arcomm.AuthorizationFailed):
        # if we get kicked out of the session... we have to make our own
        # response object... :(
        exc_type, exc_value, _ = sys.exc_info()
        err_type = exc_type.__name__
        error = "[{}] {}".format(err_type, exc_value)
        response = arcomm.Response("!" + err_type.lower(), error, errored=True)
        responses = arcomm.ResponseStore(endpoint, **kwargs)
        responses.append(response)

    return responses


class Pool:
    """Creates a pool of hosts on which to run a certain set of commands
    asynchronously"""

    def __init__(self, sessions, commands=[], callback=None, processes=None,
                 delay=0, **kwargs):

        self._processes = processes

        # delay the return of start- give slower sessions time to initialize
        self._delay = delay

        self._callback = callback

        # commands to be executed on each session
        self._commands = commands

        self._session_defaults = kwargs

        self._sessions = []
        self.load_sessions(sessions)

        self._results = []

        self._pool = mp.Pool(self._processes) # , _prep_worker)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        self.join()
        pass

    def __iter__(self):
        for item in self._results:
            yield item.get()

    @property
    def size(self):
        return self._size

    @property
    def delay(self):
        return self._delay

    @property
    def sessions(self):
        return self._sessions


    @property
    def results(self):
        return self._results

    def load_sessions(self, sessions):

        for session in sessions:
            params = {}
            if isinstance(session, (tuple, list)):
                session, params = session

            self.add_session(session, **params)

    def add_session(self, endpoint, **kwargs):

        params = kwargs.copy()
        params.update(self._session_defaults)
        self._sessions.append((endpoint, params))

    def start(self):

        for endpoint, params in self._sessions:
            args = (endpoint, self._commands)
            result = self._pool.apply_async(_worker, args, params,
                                            callback=self._callback)
            self._results.append(result)

        time.sleep(self._delay)

    def join(self):
        self._pool.join()

    def close(self):
        self._pool.close()

    def kill(self):
        """Terminate the pool and empty the queue"""
        self._pool.terminate()
