import pytest
import re
import arcomm


HOSTS = ["spine1a", "spine2a"]

def test_startup(creds):
    print creds