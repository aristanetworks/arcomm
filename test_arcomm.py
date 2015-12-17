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

def test_invalid_host():
    pass

def test_execute_ok(protocol):
    response = arcomm.execute(HOST, ['show clock'], protocol=protocol)

def test_execute_sess():
    conn = arcomm.connect(HOST, creds=ADMIN_CREDS)
    arcomm.execute(conn, 'show version')

def test_execute_bad_auth(protocol):
    with pytest.raises(arcomm.AuthenticationFailed):
        arcomm.connect(HOST, creds=arcomm.BasicCreds('jerk', 'store'),
            protocol=protocol)

def test_execute_bad_command(protocol):
    response = arcomm.execute(HOST, ['show gloc'], protocol=protocol)
    assert response.status == 'failed'

def test_not_authorized(protocol):
    response = arcomm.execute(HOST, ['show running-config'],
                              creds=OPS_CREDS, protocol=protocol)

    assert response.status == 'failed'

def test_authorize(protocol):
    response = arcomm.execute(HOST, ['show running-config'], creds=OPS_CREDS,
        authorize=ENABLE_SECRET, protocol=protocol)

def test_execute_eapi_unconverted_command():

    response = arcomm.execute(HOST, ['show clock'], encoding='json',
                              protocol='eapi+http')
    assert response.status == 'failed'

def test_response_store_access():
    responses = arcomm.execute(HOST, ['show clock', 'show version'],
        encoding='text')
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

    sess = arcomm.Session(HOST, creds=OPS_CREDS, protocol='ssh')
    sess.connect()
    cloned = sess.clone('vswitch1', protocol='eapi')
    assert cloned.hostname != sess.hostname
    assert cloned._conn != sess._conn
    # for item in sess.__dict__.keys():
    #     if item == '_conn':
    #         assert getattr(sess, item) != getattr(cloned, item)
    #     else:
    #         assert getattr(sess, item) == getattr(cloned, item)

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
    assert arcomm.configure(conn, ['ip host dummy localhost',
                                   'no ip host dummy'])
    assert arcomm.execute_pool([HOST], creds, commands)
    assert arcomm.execute_bg(HOST, creds, commands)
    assert arcomm.execute_once(HOST, creds, commands)

    arcomm.execute_until(conn, commands, condition=r'\:[0-5]0',
                         timeout=11, sleep=.1)

    arcomm.close(conn)
