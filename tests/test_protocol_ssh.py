import pytest
import re
# from arcomm.api import authorize, configure, connect_with_password, \
#                  connect_with_uri, connect, create_uri, execute, \
#                  execute_until, get_credentials

from arcomm.session import Session
from arcomm.exceptions import AuthenticationFailed, AuthorizationFailed, \
                              ExecuteFailed

# def test_authorize_nosecret(session):
#
#     try:
#         session.super()
#     except AuthorizationFailed as e:
#         pass
#
#     assert not session.authorized

# def test_authorize_badsecret(connection):
#
#     execute(connection, "disable")
#     connection._authorized = False
#
#     try:
#         authorize(connection, BAD_SECRET)
#     except AuthorizationFailed as e:
#         pass
#
#     assert not connection.authorized

# def test_authorize_secret(connection):
#
#     execute(connection, "disable")
#     connection._authorized = False
#
#     authorize(connection, SECRET)
#     assert connection.authorized

def test_execute(session):

    response = connection.send('show clock')
    assert response

# def test_execute_prompt(connection):
#     authorize(connection, SECRET)
#
#     # make switch prompt user to confirm
#     execute(connection, "no terminal dont-ask")
#
#     try:
#         response = execute(connection, dict(cmd="write erase", prompt=re.compile(r"confirm"), answer=""))
#     finally:
#         # cleanup
#         execute(connection, ["terminal dont-ask", "write"])
