# -*- coding: utf-8 -*-
import arcomm
import pytest

# @pytest.mark.parametrize("protocol,timeout", [
#     ("ssh", 30),
#     ("capi", 30)
# ])
#def test_connect(proto, timeout, device, creds):
PROTOCOLS = ["ssh", "capi"]
@pytest.fixture(scope="module", params=PROTOCOLS)
def connection(host, creds, request):
    return arcomm.connect(host, creds, protocol=request.param)

def test_authorize(connection, authorize_password):
    arcomm.authorize(connection, secret=authorize_password)
    assert arcomm.authorized(connection)

@pytest.mark.parametrize("protocol,timeout", [("ssh", 30), ("capi", 30)])
def test_clone(connection, host, creds, protocol, timeout):
    conn = arcomm.clone(connection)
    conn = arcomm.clone(connection, host=host)
    conn = arcomm.clone(connection, creds=creds)
    conn = arcomm.clone(connection, protocol=protocol)
    conn = arcomm.clone(connection, timeout=10)
    assert connection.timeout == 10
    arcomm.clone(connection, host=None, creds=creds, protocol=request.param)
#
# def test_close():
#     arcomm.close(connection)
#
# def test_configure():
#     arcomm.configure(connection, commands, *args, **kwargs)
#
# def test_connect():
#     arcomm.connect(host, creds, protocol=None, timeout=None, **kwargs)
#
# def connect_with_password():
#     arcomm.connect_with_password(host, username, password="", **kwargs)
#
# def test_connect_with_uri():
#     connect_uri(uri, **kwargs)
#
# def test_create_uri():
#     arcomm.create_uri(host, protocol, username, password, port)
#
# def test_create_pool():
#     arcomm.create_pool(hosts, creds, commands, **kwargs)
#
# def test_execute():
#     arcomm.execute(connection, commands)
#
# def test_execute_bg():
#     arcomm.execute_bg(host, creds, commands, **kwargs)
#
# def test_execute_once():
#     arcomm.execute_once(host, creds, commands)
#
# def test_execute_pool():
#     arcomm.execute_pool(hosts, creds, commands, **kwargs)
#
# def test_execute_until():
#     arcomm.execute_until(connection, commands, condition, timeout=30, sleep=5,
#                   exclude=False)
#
# def test_get_credentials():
#     arcomm.get_credentials(username, password="", authorize_password=None,
#                     private_key=None)

