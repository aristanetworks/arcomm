# -*- coding: utf-8 -*-
import arcomm
import pytest

def test_authorize(connection, authorize_password):
    arcomm.authorize(connection, secret=authorize_password)
    assert arcomm.authorized(connection)

@pytest.mark.parametrize("protocol,timeout", [("ssh", 30), ("eapi", 30)])
def test_clone(connection, host, creds, protocol, timeout):
    conn = arcomm.clone(connection)
    conn = arcomm.clone(connection, host=host)
    conn = arcomm.clone(connection, creds=creds)
    conn = arcomm.clone(connection, protocol=protocol)
    assert conn.protocol == protocol
    conn = arcomm.clone(connection, timeout=10)
    assert conn.timeout == 10
#
def test_configure(connection, configure_commands):
    print arcomm.configure(connection, configure_commands)

def test_connect_with_password(host, creds, exec_commands):
    conn = arcomm.connect_with_password(host, creds.username,
                                        password=creds.password)
    conn.execute(exec_commands)

def test_connect_with_uri(host, creds, exec_commands, protocol="eapi", port=80):
    uri = arcomm.create_uri(host, protocol, creds.username, creds.password,
                            port)
    conn = arcomm.connect_uri(uri)
    conn.execute(exec_commands)

def test_create_pool(hosts, creds, exec_commands):
    pool = arcomm.create_pool(hosts, creds, exec_commands)
    pool.start()
    pool.join()
    assert pool.results

def test_execute(connection, exec_commands):
    arcomm.execute(connection, exec_commands)

def test_execute_bg(connection, exec_commands):
    arcomm.execute_bg(connection, exec_commands)

def test_execute_once(host, creds, exec_commands):
    arcomm.execute_once(host, creds, exec_commands)

def test_execute_pool(hosts, creds, exec_commands):
    for response in arcomm.execute_pool(hosts, creds, exec_commands):
        pass
#
def test_execute_until(connection):
    commands = ["show version"]
    condition = r"i386"
    response = arcomm.execute_until(connection, commands, condition, timeout=30,
                                    sleep=5, exclude=False)

def test_close(connection):
    arcomm.close(connection)
