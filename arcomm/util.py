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

def deepmerge(source, destination):
    for key, value in source.iteritems():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            _merge(value, node)
        else:
            destination[key] = value

    return destination

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
        'hostname': env.ARCOMM_DEFAULT_HOST,
        'protocol': env.ARCOMM_DEFAULT_PROTOCOL,
        'timeout': env.ARCOMM_DEFAULT_TIMEOUT,
        'creds': BasicCreds(env.ARCOMM_DEFAULT_USERNAME,
                            env.ARCOMM_DEFAULT_PASSWORD)
    }

def parse_endpoint(uri, use_defaults=True):

    result = {}
    # look for a bare hostname
    match = re.match(r'^([\w\-\.]+)$', uri)
    if match:
        result['hostname'] = match.group(1)
    else:
        parsed = urlparse.urlparse(uri)
        if parsed.hostname:
            result['hostname'] = parsed.hostname
        if parsed.scheme:
            result['protocol'] = parsed.scheme

        if parsed.username:
            _pass = ''
            if parsed.password:
                _pass = parsed.password
            result['creds'] = BasicCreds(parsed.username, _pass)
        if parsed.port:
            result['port'] = parsed.port
        if parsed.path:
            result['path'] = parsed.path

    if use_defaults:
        result = merge_dicts(session_defaults(), result)

    return result

def load_endpoints(path):
    endpoints = []

    with open(path, 'r') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if re.search(r"^\s*(#|!)", line):
                continue
            match = re.search(r"(?:[a-f0-9:.]+\s+)?(\S+)", line, re.IGNORECASE)
            if match:
                line = match.group(1)

            endpoints.append(line)

    return endpoints

def mpop(lst, length, offset=0):
    popped = []
    for _ in range(offset, length+offset):
        # always pop from offset.
        popped.append(lst.pop(offset))
    return popped
