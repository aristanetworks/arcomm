#!/usr/bin/env python
"""
Copyright (c) 2013 Arista Networks, Inc.  All rights reserved.
Arista Networks, Inc. Confidential and Proprietary.
"""

import sys
import os
from setuptools import setup, find_packages

if sys.version_info < (2, 7, 0):
    raise NotImplementedError("Sorry, you need at least Python 2.7 to install.")

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from arcomm import __version__

readme = open('README.md').read()

setup(
    name = "arcomm",
    version = __version__,
    author = "Jesse Mather",
    author_email = "jmather@arista.com",
    description = "Library for controlling to Arista switches",
    long_description = readme,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Arista Test Engineers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Environment :: Network Automation"
    ],
    packages = find_packages(),
    url = "http://aristanetworks.com",
    license = "Proprietary",
    install_requires = ["jsonrpclib", "paramiko"],
    entry_points = {
        'console_scripts': [
            'arcomm = arcomm.console:main',
        ]
    }
)
