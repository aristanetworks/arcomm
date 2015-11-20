# -*- coding: utf-8 -*-
"""Utility helper functions and shortcuts"""
import re

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import arcomm.env as env
from arcomm.credentials import BasicCreds

def to_list(data):
    """Creates a list containing the data as a single element or a new list
    from the original if it is already a list or a tuple"""
    if isinstance(data, (list, tuple)):
        return list(data)
    elif data is not None:
        return [data]
    else:
        return []


def to_multiline_string(data, end_of_line="\r\n"):
    """Return a string from a list"""

    if hasattr(data, "__iter__"):
        data = end_of_line.join(data)

    return data

def merge_dicts(*args):
    merged = args[0]
    for dict_ in args[1:]:
        merged.update(dict_)
    return merged
dictmerge = merge_dicts

def indentblock(text, spaces=0):
    text = text.splitlines() if hasattr(text, "splitlines") else []
    return "\n".join([" " * spaces + line for line in text])

def to_commands(commands):
    """Converts a command or list of commands to a list of Command objects"""
    commands = to_list(commands)
    _loc = []
    for _cmd in commands:
        if not isinstance(_cmd, Command):
            if re.search("^(!|#)", _cmd) or re.search("^\s*$", _cmd):
                continue
            _cmd = Command(_cmd.strip())
        _loc.append(_cmd)
    return _loc

def session_defaults():
    return {
        'host': env.ARCOMM_DEFAULT_HOST,
        'protocol': env.ARCOMM_DEFAULT_PROTOCOL,
        'timeout': env.ARCOMM_DEFAULT_TIMEOUT,
        'creds': (env.ARCOMM_DEFAULT_USERNAME, env.ARCOMM_DEFAULT_PASSWORD),
        'super': (env.ARCOMM_DEFAULT_SUPER, env.ARCOMM_DEFAULT_SUPASS)
    }

def parse_uri(uri=None):
    """handel uri or bare hostname"""

    defaults = session_defaults()
    protocol = defaults['protocol']
    creds = defaults['creds']

    hostname = defaults['host']
    transport = None
    path = ''
    port = None

    if uri:
        match = re.match(r'^([\w\-]+)$', uri)
        if match:
            hostname = match.group(1)
        else:
            parsed = urlparse.urlparse(uri)
            hostname = parsed.hostname or hostname
            protocol = parsed.scheme or protocol
            username = parsed.username or creds[0]
            password = parsed.password or creds[1]
            creds = (username, password)
            port = parsed.port
            path = parsed.path

    if '+' in protocol:
        protocol, transport = protocol.split('+', 1)

    return {
        'creds': BasicCreds(creds[0], creds[1]),
        'hostname': hostname,
        'path': path,
        'port': port,
        'protocol': protocol,
        'transport': transport
    }
