# -*- coding: utf-8 -*-
"""Utility helper functions and shortcuts"""

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
    
def dictmerge(*args):
    """Merge dictionarys"""
    result = {}
    for dict_ in args:
        result = dict(list(result.items()) + list(dict_.items()))
    return result