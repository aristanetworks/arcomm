import pytest
from arcomm.api import authorize, configure, connect_with_password, \
                 connect_with_uri, connect, create_uri, execute, \
                 execute_until, get_credentials

from arcomm.exceptions import AuthenticationFailed, AuthorizationFailed, \
                              ExecuteFailed, Timeout

HOST = "spine2a"
USER = "admin"
PASS = ""
BAD_SECRET = "badsecret"
SECRET = "s3cr3t"

@pytest.fixture(scope="module")
def connection():
    return connect(HOST, get_credentials(username=USER, password=PASS), protocol="ssh")

def test_authorize_nosecret(connection):

    try:
        authorize(connection)
    except AuthorizationFailed as e:
        pass

    assert not connection.authorized

def test_authorize_badsecret(connection):

    execute(connection, "disable")
    connection._authorized = False

    try:
        authorize(connection, BAD_SECRET)
    except AuthorizationFailed as e:
        pass

    assert not connection.authorized

def test_authorize_secret(connection):

    execute(connection, "disable")
    connection._authorized = False

    authorize(connection, SECRET)
    assert connection.authorized

def test_execute(connection):

    response = execute(connection, "show version")
    assert response

def test_execute_prompt(connection):
    authorize(connection, SECRET)

    # make switch prompt user to confirm
    execute(connection, "no terminal dont-ask")

    try:
        response = execute(connection, dict(cmd="write erase", input=""))
    finally:
        # cleanup
        execute(connection, ["write", "terminal dont-ask"])
