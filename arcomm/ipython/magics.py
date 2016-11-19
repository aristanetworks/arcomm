#
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
IPython Magic functions for Arcomm
"""

import arcomm
import argparse
import re
from getpass import getpass, getuser

from IPython.core import magic_arguments
from IPython.core.display import display_pretty, display
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic,
                                line_cell_magic, on_off, needs_local_scope)

@magics_class
class ArcommMagics(Magics):

    def __init__(self, shell, **kwargs):
        super().__init__(shell, **kwargs)
        self._connections = []

    @needs_local_scope
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('endpoints', nargs="*",
        help="""Host(s) to connect to"""
    )
    @magic_arguments.argument('-a', '--askpass', action="store_true",
        help="""Force prompt for password."""
    )
    @magic_arguments.argument('-e', '--encoding', default="text",
        choices=["text", "json"],
        help="""Specify output encoding: json or text"""
    )
    @magic_arguments.argument('-c', '--command',
        help="""Command to send to host"""
    )
    @line_cell_magic
    def arcomm(self, line, cell=None, local_ns={}):

        args = magic_arguments.parse_argstring(self.arcomm, line)
        commands = []
        responses = []

        if args.command:
            commands = [args.command]
        elif cell:
            commands = [cmd for cmd in cell.splitlines()]
        for endpoint in args.endpoints:
            reuse = [conn for conn in self._connections if conn.hostname == endpoint]

            if reuse:
                conn = reuse[0]
            else:
                conn = arcomm.connect(endpoint, askpass=args.askpass)
                self._connections.append(conn)

            if commands:
                response = conn.send(commands, encoding=args.encoding)
                responses.append(response)

        return responses

    @magic_arguments.magic_arguments()
    @magic_arguments.argument('hostname', nargs="*",
        help="""Host(s) to connect to"""
    )
    @magic_arguments.argument('-u', '--username',
        help="""Username for connection"""
    )
    @magic_arguments.argument('-p', '--password', default="",
        help="""Password for connection"""
    )
    @line_magic
    def arconnect(self, line):

        args = magic_arguments.parse_argstring(self.arconnect, line)

        for hostname in args.hostname:
            if not args.username:
                args.username = getuser()

            if not args.password:
                _prompt = "{}@{}'s password: ".format(args.username, hostname)
                args.password = getpass(_prompt) or ""

            conn = arcomm.connect(hostname, creds=(args.username, args.password))
            self._connections[hostname] = conn

        #return self._connections

    @magic_arguments.magic_arguments()
    @magic_arguments.argument('connections', nargs="*",
        help="""Select existing connection by hostname"""
    )
    @magic_arguments.argument('-e', '--encoding', default="text",
        choices=["text", "json"],
        help="""Specify output encoding: json or text"""
    )
    @magic_arguments.argument('-c', '--command',
        help="""Commands to send to host"""
    )
    @magic_arguments.argument('--no-display', action="store_true",
        help="""Skip printing responses"""
    )
    @magic_arguments.argument('--capture', action="store_true", default=True,
        help="""Specify whether to return responses [default: True]"""
    )
    @line_cell_magic
    def arsends(self, line, cell=None):

        args = magic_arguments.parse_argstring(self.arsends, line)

        responses = []
        if args.command:
            args.command = [args.command]
        else:
            cell_cmds = [cmd for cmd in cell.splitlines()]
            args.command = cell_cmds

        commands = [re.sub("(?:^\"|\"$)", "", cmd) for cmd in args.command]

        for name in args.connections:
            conn = self._connections.get(name, None)
            if not conn:
                raise ValueError("Connection to '{}' does not exist".format(conn))
            response = conn.send(commands, encoding=args.encoding)
            responses.append(response)

            if not args.no_display:
                # if args.encoding == "text":
                #     print(response.to_yaml())
                # else:
                #     print(response)
                print(response)

        return responses

def load_ipython_extension(shell):
    '''Registers the skip magic when the extension loads.'''
    shell.register_magics(ArcommMagics)

def unload_ipython_extension(shell):
    '''Unregisters the skip magic when the extension unloads.'''
    pass
