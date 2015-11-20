import pytest
#from arcomm import Creds
from arcomm.session import Session

# PROTOCOLS = ["ssh", "eapi"]
# READONLY_CREDS = ("nocuser", "nocuser")
# CREDS = ("admin", "")
# ENABLE_SECRECT = ("s3cr3t")

PROTOCOL = 'ssh'
HOST = 'vswitch1'
USER = 'admin'
PASS = 'admin'
CREDS = (USER, PASS)
#BAD_SECRET = 'badsecret'
SUPER = ('', '')
URI = '{}://{}'.format(PROTOCOL, HOST)
URI_AUTH = '{}://{}:{}@{}'.format(PROTOCOL, USER, PASS, HOST)

def pytest_addoption(parser):
    group = parser.getgroup("arcomm", "Arcomm testing options")
    group.addoption('--uri', action="append",
                    help="Host to use for testing")
    group.addoption('--login', default='admin',
                    help="Specifies username on host")
    group.addoption('--password', default='')
    group.addoption('--super-password')

@pytest.fixture(scope="session")
def uris(request):
    """Host hostname or IP address"""
    return request.config.getoption("--uri")

@pytest.fixture(scope="session")
def uri(request, uris):
    """Host hostname or IP address"""
    return uris[0]


@pytest.fixture(scope="session")
def login(request):
    """Password for user on host"""
    return request.config.getoption("--login")

@pytest.fixture(scope="session")
def password(request):
    """Username on host"""
    return request.config.getoption("--password")


# @pytest.fixture(scope="session")
# def authorize_password(request):
#     """Enable secret used to gain privileged access"""
#     return request.config.getoption("--authorize-password")
#
@pytest.fixture(scope='session')
def creds(login, password):
    """Return a credentials object, used with connect"""
    #authorize_password = request.config.getoption("--authorize-password")
    return (login, password)

# @pytest.fixture(scope="session")
# def readonly_creds():
#     username, password = READONLY_CREDS
#     return arcomm.get_credentials(username=username, password=password)
#

@pytest.fixture(scope='module')
def session(uri, creds, request):
    sess = Session()
    return sess.connect(uri, creds)

@pytest.fixture(scope="session")
def exec_commands():
    return ["show version", "show clock"]

@pytest.fixture(scope="session")
def configure_commands():
    return ["ip host dummy 127.0.0.1", "ping dummy", "no ip host dummy"]
