# -*- coding: utf-8 -*-
"""Utility helper functions and shortcuts"""


def to_list(data):
    """Creates a list containing the data as a single element or a new list
    from the original if it is already a list or a tuple"""
    if isinstance(data, (list, tuple)):
        return list(data)
    else:
        return [data]

def to_multiline_string(data, end_of_line="\r\n"):
    """Return a string from a list"""

    if hasattr(data, "__iter__"):
        data = end_of_line.join(data)

    return data

def to_list_of_commands(commands):
    """Converis a command or list of commands (strings) to a list of command
    objects"""
    commands = to_list(commands)
    list_of_commmands = []
    for _cmd in commands:
        from command import Command
        if not isinstance(_cmd, Command):
            _cmd = Command(_cmd)
        list_of_commmands.append(_cmd)
    return list_of_commmands
