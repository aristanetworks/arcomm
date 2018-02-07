# -*- coding: utf-8 -*-

import arcomm

def test_authorize(hostaddr, creds):
    pass

def test_authorized():
    pass

def test_background():
    pass

def test_batch():
    pass

def test_clone():
    pass

def test_close():
    pass

def test_configure():
    pass

def test_connect():
    pass

def test_creds():
    pass

def test_execute(hostaddr, creds):
    conn = arcomm.connect(hostaddr, creds=creds)
    response = conn.execute(["show version"])

    for item in response:
        print(type(item))

def test_execute_until():
    pass

def test_get_credentials():
    pass

def test_tap():
    pass
