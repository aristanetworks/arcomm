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

def load_ipython_extension(shell):
    '''Registers the skip magic when the extension loads.'''
    shell.register_magics(ArcommMagics)

def unload_ipython_extension(shell):
    '''Unregisters the skip magic when the extension unloads.'''
    pass
