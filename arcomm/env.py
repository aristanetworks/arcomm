# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
read env variables or use sensible defaults
"""
import os

ARCOMM_DEFAULT_PROTOCOL = 'eapi+http'
ARCOMM_DEFAULT_TIMEOUT  = 30
ARCOMM_DEFAULT_USERNAME = 'admin'
ARCOMM_DEFAULT_PASSWORD = ''
ARCOMM_DEFAULT_SUPER = ''
ARCOMM_DEFAULT_SUPASS = ''

if os.name == 'nt':
    ARCOMM_CONF_DIR = os.path.join(os.getenv('APPDATA'), 'arcomm')
else:
    # this will apply to both posix and java
    ARCOMM_CONF_DIR = os.path.expanduser('~/.arcomm')

ARCOMM_SECRETS_FILE = os.path.join(ARCOMM_CONF_DIR, 'secrets.yml')
