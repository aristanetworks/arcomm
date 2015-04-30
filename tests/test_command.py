# -*- coding: utf-8 -*-
import pytest
from arcomm.command import Command

KEYS = ["cmd", "prompt", "answer"]

@pytest.fixture(scope="module")
def command():
    return Command("enable", prompt=r"password\:", answer="asdasda")

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