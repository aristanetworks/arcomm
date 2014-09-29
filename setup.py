#!/usr/bin/env python
"""
Copyright (c) 2014 Arista Networks, Inc.  All rights reserved.
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
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Terminals"
    ],
    packages = find_packages(),
    url = "https://github.com/aristanetworks/arcomm",
    download_url = "https://github.com/aristanetworks/arcomm/archive/v1.0.0.tar.gz",
    license = "MIT Licesnse",
    install_requires = ["jsonrpclib", "paramiko"],
    entry_points = {
        'console_scripts': [
            'arcomm = arcomm.console:main',
        ]
    }
)
