import pytest
from arcomm.protocols.eapi import Eapi

@pytest.fixture(scope="module")
def conn(host, creds):
    conn = Eapi(host, creds)
    conn.connect()
    return conn

def test_eapi_authorize(conn):
    conn.authorize()

def test_eapi_execute(conn):
    conn.execute("show version")
    conn.execute(["show version", "show clock"])

def test_eapi_execute_bogus(conn):
    conn.execute("show ice cream sandwich")
    conn.execute(["show ice cream sandwich", "show banana split",
                  "show platform pitchfork copp mapping"])
