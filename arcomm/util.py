# -*- coding: utf-8 -*-
# Copyright (c) 2014 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
"""
Utility helper functions and shortcuts
"""
def to_list(data):
    """Creates a list containing the data as a single element or a new list
    from the original if it is already an iterable"""

    if not hasattr(data, "__iter__"):
        data = [] if data is None else [data]
    return list(data)

def to_multiline_string(data, end_of_line="\r\n"):
    """Return a string from a list"""

    if hasattr(data, "__iter__"):
        data = end_of_line.join(data)

    return data
