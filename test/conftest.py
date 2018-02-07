# -*- coding: utf-8 -*-
# Copyright (c) 2018 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import pytest

def pytest_addoption(parser):
    parser.addoption("--hostaddr", help="specifies target device")
    parser.addoption("--username", help="specifies username on target device")
    parser.addoption("--password", help="specifies password on target device")
    # parser.addoption("--certificate", help="client certificate file")
    # parser.addoption("--private-key", help="client privatr key file")

@pytest.fixture(scope="session", autouse=True)
def hostaddr(request):
    return request.config.getoption("hostaddr")

# @pytest.fixture(scope="session", autouse=True)
# def cert(request):
#     if request.config.getoption("certificate"):
#         return (request.config.getoption("certificate"),
#                 request.config.getoption("private_key"))

@pytest.fixture(scope="session", autouse=True)
def creds(request):
    return (request.config.getoption("username"),
            request.config.getoption("password"))
