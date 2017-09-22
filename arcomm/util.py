# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Utility helper functions and shortcuts"""
import re

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import arcomm.env as env
from arcomm.credentials import BasicCreds

from future.utils import iteritems

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

# def deepmerge(source, destination):
#     for (key, value) in iteritems(source):
#         if isinstance(value, dict):
#             # get node or create one
#             node = destination.setdefault(key, {})
#             _merge(value, node)
#         else:
#             destination[key] = value
#
#     return destination

def indentblock(text, spaces=0):
    """Indent multiple lines of text to the same level"""
    text = text.splitlines() if hasattr(text, 'splitlines') else []
    return '\n'.join([' ' * spaces + line for line in text])

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

def parse_endpoint(uri):

    protocol_re = r'([\w\+\-]+)?://'
    creds_re = r'(?:([\w\-\_]+)(?:\:([\S]+))?@)?'
    host_re =  (
        r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?(?:\.)?)+(?:[A-Z]{2,6}\.?|'
        r'[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    )
    port_re = r'(?::(\d+))?'

    regex = re.compile(r'^' + protocol_re + creds_re + host_re + port_re + r'$',
        re.IGNORECASE)
    match = regex.match(uri)

    if not match:
        # try and match on bare hostname.
        # NOTE: $. is a pattern that will never match a in a single-line regex.
        #       I'm using it here to 'fill out' the match groups.
        regex = re.compile(r'^($.)?($.)?($.)?' + host_re + r'($.)?$',
            re.IGNORECASE)
        match = regex.match(uri)

    # if we still don't have a match...
    if not match:
        raise ValueError("Invalid URI string:", uri)

    keys = ('protocol', 'username', 'password', 'hostname', 'port')
    parsed = dict(zip(keys, match.groups()))

    if parsed["port"]:
        parsed["port"] = int(parsed["port"])

    return parsed

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

def zipnpad(keys, values, default=None):
    """zips two lits and pads the second to match the first"""

    keys_len = len(keys)
    values_len = len(values)

    if (keys_len < values_len):
        raise ValueError("keys must be as long or longer than values")

    values += [default] * (keys_len - values_len)
    
    return zip(keys, values)
