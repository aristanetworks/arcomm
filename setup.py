#!/usr/bin/env python
"""
Copyright (c) 2014 Arista Networks, Inc.  All rights reserved.
Arista Networks, Inc. Confidential and Proprietary.
"""

# import sys
# import os
# from setuptools import setup, find_packages
#
# if sys.version_info < (2, 7, 0):
#     raise NotImplementedError("Sorry, you need at least Python 2.7 to install.")
#
# sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
# from arcomm import __version__
#
# readme = open('README.rst').read()
#
# setup(
#     name = "arcomm",
#     version = __version__,
#     author = "Jesse Mather",
#     author_email = "jmather@arista.com",
#     maintainer=
#     maintainer_email=
#     description = "Library for connecting to Arista switches",
#     long_description = readme,
#     classifiers = [
#         "Development Status :: 3 - Alpha",
#         "Environment :: Console",
#         "Intended Audience :: Information Technology",
#         "License :: OSI Approved :: MIT License",
#         "Natural Language :: English",
#         "Operating System :: OS Independent",
#         "Programming Language :: Python",
#         "Programming Language :: Python :: 2.7",
#         "Topic :: Software Development :: Libraries :: Python Modules",
#         "Topic :: Software Development :: Testing",
#         "Topic :: Terminals"
#     ],
#     packages = find_packages(),
#     install_requires = ["requests"],
#     url = "https://github.com/aristanetworks/arcomm",
#     license = "MIT Licesnse",
#     entry_points = {
#         'console_scripts': [
#             'arcomm = arcomm.entry:main',
#         ]
#     }
# )


import codecs
import os
import re

from setuptools import setup, find_packages


###################################################################

NAME = "arcomm"
PACKAGES = find_packages(
META_PATH = os.path.join(NAME, "__init__.py")
KEYWORDS = ["arista", "eapi", "ssh"]
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Information Technology",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development :: Testing",
    "Topic :: Terminals"
]
INSTALL_REQUIRES = ['requests']

###################################################################

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


META_FILE = read(META_PATH)

def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


if __name__ == "__main__":
    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=find_meta("uri"),
        version=find_meta("version"),
        author=find_meta("author"),
        author_email=find_meta("email"),
        maintainer=find_meta("author"),
        maintainer_email=find_meta("email"),
        keywords=KEYWORDS,
        long_description=read("README.rst"),
        packages=PACKAGES,
        #package_dir={"": "src"},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
    )
