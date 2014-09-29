# -*- coding: utf-8 -*-
import arcomm
import pytest

@pytest.mark.parametrize("proto,timeout", [
    ("ssh", 30),
    ("capi", 30)
])
def test_connect(proto, timeout, device, creds):
    conn = arcomm.connect(device, creds=creds, protocol=proto, timeout=timeout)
    assert conn.connected, "connnection was not made"

@pytest.mark.parametrize("proto,timeout", [
    ("ssh", 30),
    ("capi", 30)
])
def test_authorize(proto, timeout, device, creds):
    conn = arcomm.connect(device, creds=creds, protocol=proto, timeout=timeout)
    arcomm.authorize(conn, creds.authorize_password)
    
    assert arcomm.authorized(conn), "connection is not authorized"

def test_close():
    pass