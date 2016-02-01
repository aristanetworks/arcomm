# -*- coding: utf-8 -*-
import arcomm
import pytest
import os

from pprint import pprint

"""
"""

NXHOST = 'bogus'
ADMIN_CREDS = arcomm.BasicCreds('admin', '')
OPS_CREDS = arcomm.BasicCreds('ops', 'ops!')
ENABLE_SECRET = 's3cr3t'
HOST = os.environ.get('ARCOMM_HOST', 'veos')

#
# @pytest.fixture(scope='module', autouse=True)
# def init_dut():
#     pass

arcomm.env.ARCOMM_DEFAULT_PROTOCOL = 'mock'

@pytest.fixture(scope='module', autouse=True) #, params=['eapi+http', 'ssh'])
def protocol(request):
    return arcomm.env.ARCOMM_DEFAULT_PROTOCOL #request.param

def test_entry():

    arcomm.execute
    arcomm.background
    arcomm.batch
    arcomm.configure
    arcomm.connect
    arcomm.session

    arcomm.ResponseStore
    arcomm.Response
    arcomm.ConnectFailed
    arcomm.AuthenticationFailed
    arcomm.AuthorizationFailed
    arcomm.ExecuteFailed

def test_uri_parsing():
    pe = arcomm.util.parse_endpoint
    print
    pprint(arcomm.Session('eapi://vswitch1'))
    pprint(arcomm.Session('eapi+http://vswitch1'))
    pprint(arcomm.Session('eapi+https://vswitch1'))

def test_execute_ok(protocol):
    response = arcomm.execute(HOST, ['show clock'], protocol=protocol)

def test_execute_sess():
    conn = arcomm.connect(HOST, creds=ADMIN_CREDS)
    arcomm.execute(conn, 'show version')

def test_bad_auth(protocol):
    with pytest.raises(arcomm.AuthenticationFailed):
        arcomm.connect(HOST, creds=arcomm.BasicCreds('baduser', 'badpass'),
            protocol=protocol)

def test_execute_invalid_command(protocol):
    response = arcomm.execute(HOST, ['show bogus'], protocol=protocol)
    assert response.status == 'failed'

def test_execute_not_authorized(protocol):

    with pytest.raises(arcomm.AuthorizationFailed):
        arcomm.execute(HOST, ['show restricted'], authorize=('bad', 'bad'))

    response = arcomm.execute(HOST, ['show restricted'])
    assert response.status == 'failed' and 'not authorized' in str(response)

def test_authorize(protocol):
    response = arcomm.execute(HOST, ['show running-config'], creds=OPS_CREDS,
        authorize=ENABLE_SECRET, protocol=protocol)

# def test_execute_eapi_unconverted_command():
#
#     response = arcomm.execute(HOST, ['show clock'], encoding='json',
#                               protocol='eapi+http')
#     assert response.status == 'failed'

def test_response_store_access():
    responses = arcomm.execute(HOST, ['show version'])
    assert hasattr(responses, '__iter__'), "response must be an iterable"
    assert responses.last().command == 'show version', \
        "Last item should have been 'show version'"

    for r in responses:
        assert hasattr(r, 'command')
        assert hasattr(r, 'output')

def test_background(protocol):

    did_stuff = False
    with arcomm.background(HOST, ['show running-config all'],
                           protocol=protocol) as proc:
        did_stuff = True

    assert did_stuff

    for res in proc.results:
        assert isinstance(res, arcomm.ResponseStore)

def test_batch(protocol):
    for res in arcomm.batch([HOST, HOST], ['show version'], protocol=protocol):
        assert isinstance(res, arcomm.ResponseStore)

def test_mixin_until():
    with arcomm.Session(HOST, creds=ADMIN_CREDS) as sess:
        sess.execute_until(['show clock'], condition=r'\:[0-5]0', timeout=30,
                           sleep=.1)

        with pytest.raises(ValueError):
            sess.execute_while(['show version'], condition=r'.*', timeout=5,
                               sleep=1)

def test_tap():
    class _Mark(object): pass

    bob = _Mark()
    def callback(result):
        #print result
        bob.was_here = True

    result = arcomm.tap(callback, arcomm.execute, 'veos', 'show version')
    assert hasattr(bob, 'was_here')

def test_clone():

    sess = arcomm.Session(HOST, creds=OPS_CREDS)
    sess.connect()
    cloned = sess.clone('other')
    assert cloned.hostname != sess.hostname
    assert cloned._conn != sess._conn

def test_oldway_funcs():

    username = ADMIN_CREDS.username
    password = ADMIN_CREDS.password

    creds = arcomm.get_credentials(username, password)
    commands = ['show clock']
    conn = arcomm.connect(HOST, creds)
    assert conn
    arcomm.authorize(conn)
    assert arcomm.authorized(conn)
    assert arcomm.clone(conn)
    assert arcomm.configure(conn, [])
    assert arcomm.execute_pool([HOST], creds, commands)
    assert arcomm.execute_bg(HOST, creds, commands)
    assert arcomm.execute_once(HOST, creds, commands)

    arcomm.execute_until(conn, commands, condition=r'\:[0-5]0',
                         timeout=11, sleep=.1)

    arcomm.close(conn)

def test_response_slice(protocol):
    response = arcomm.execute(HOST, ['show version'], protocol=protocol)
    response[0][0:5]
    response[0][0:5:2]

def test_raise_for_error(protocol):
    response = arcomm.execute(HOST, ['show bogus'], protocol=protocol)
    with pytest.raises(arcomm.ExecuteFailed):
        response.raise_for_error()

called_back = False
def test_callback(protocol):

    def _cb(response):
        global called_back
        assert isinstance(response, arcomm.response.Response)
        called_back = True

    response = arcomm.execute(HOST, ['show bogus'], protocol=protocol,
                              callback=_cb)

    assert called_back
