# -*- coding: utf-8 -*-

import os
import select
import sys

try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer

import paramiko

class ForwardServer(SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

class ForwardHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        chan = self.ssh_transport.open_channel('direct-tcpip',
                                               (self.chain_host, self.chain_port),
                                               self.request.getpeername())

        if chan is None:
            return

        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)

            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        chan.close()
        self.request.close()

def _open_tunnel(transport, chain):
    local_port, remote_host, remote_port = chain
    class _Hander(ForwardHandler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport
    fwd = ForwardServer(('localhost', local_port), _Hander)
    print fwd.socket.getsockname()
    fwd.serve_forever()

class SshTunnel(object):

    def __init__(self, host, creds, chain, ssh_port=22):
        self.host = host
        self.creds = creds
        self.ssh_port = ssh_port
        self.chain = chain
        self._ssh = None

    def _init_client(self):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return client

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def open(self):
        self._connect()
        _open_tunnel(self._ssh.get_transport(), self.chain)

    def _connect(self):
        self._ssh = paramiko.SSHClient()
        self._ssh.load_system_host_keys()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        username, password  = self.creds
        self._ssh.connect(self.host, self.ssh_port,
                          #key_filename=options.keyfile,
                          username=username,
                          password=password)

    def close(self):
        pass

if __name__ == '__main__':

    tun = SshTunnel('vswitch1', ('admin', ''), (0, '0.0.0.0', 8080))
    print tun.open()
