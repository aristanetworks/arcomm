# -*- coding: utf-8 -*-
import arcomm
import pytest
import os
"""
"""

NXHOST = 'bogus'
ADMIN_CREDS = arcomm.BasicCreds('admin', '')
OPS_CREDS = arcomm.BasicCreds('ops', 'ops!')
ENABLE_SECRET = 's3cr3t'
HOST = os.environ.get('ARCOMM_HOST', 'veos')

@pytest.fixture(scope='module', autouse=True)
def init_dut():
    pass

@pytest.fixture(scope='module', params=['eapi+http', 'ssh'])
def protocol(request):
    return request.param

def test_entry():

    arcomm.execute
    arcomm.configure
    arcomm.connect
    arcomm.session
    arcomm.ResponseStore
    arcomm.Response
    arcomm.ConnectFailed
    arcomm.AuthenticationFailed
    arcomm.AuthorizationFailed
    arcomm.ExecuteFailed

def test_invalid_host():
    pass

def test_execute_ok(protocol):
    response = arcomm.execute(HOST, ['show clock'], protocol=protocol)

def test_execute_bad_auth(protocol):
    with pytest.raises(arcomm.AuthenticationFailed):
        arcomm.connect(HOST, creds=arcomm.BasicCreds('jerk', 'store'),
            protocol=protocol)

def test_execute_bad_command(protocol):
    with pytest.raises(arcomm.ExecuteFailed):
        arcomm.execute(HOST, ['show gloc'], protocol=protocol)

def test_not_authorized(protocol):
    with pytest.raises(arcomm.ExecuteFailed):
        response = arcomm.execute(HOST, ['show running-config'],
            creds=OPS_CREDS, protocol=protocol)

def test_authorize(protocol):
    response = arcomm.execute(HOST, ['show running-config'], creds=OPS_CREDS,
        authorize=ENABLE_SECRET, protocol=protocol)

def test_execute_eapi_unconverted_command():
    with pytest.raises(arcomm.ExecuteFailed):
        arcomm.execute(HOST, ['show clock'], encoding='json',
            protocol='eapi+http')

def test_response_store_access():
    responses = arcomm.execute(HOST, ['show clock', 'show version'],
        encoding='text')
    assert hasattr(responses, '__iter__'), "response must be an iterable"
    assert responses.last().command == 'show version', \
        "Last item should have been 'show version'"

    for r in responses:
        assert hasattr(r, 'command')
        assert hasattr(r, 'output')
