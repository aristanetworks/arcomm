# -*- coding: utf-8 -*-
# Copyright (c) 2014 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import pytest
from arcomm.command import Command

KEYS = ["expression", "prompt", "answer", "callback"]

@pytest.fixture(scope="module")
def command():
    def cb(data):
        return True
    return Command("enable", prompt=r"password\:", answer="asdasda", callback=cb)

def test_command_property_access(command):
    for property in KEYS:
        assert hasattr(command, property)

def test_command_key_access(command):

    # test the "get" operation default value
    assert command.get("_not_a_valid_key_blah_blah", True)

    for key in KEYS:
        assert command[key]
        assert key in command
        assert command.get(key)