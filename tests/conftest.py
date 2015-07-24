import pytest
#from arcomm import Creds
import arcomm

PROTOCOLS = ["ssh", "eapi"]
READONLY_CREDS = ("nocuser", "nocuser")
CREDS = ("admin", "")
ENABLE_SECRECT = ("s3cr3t")

def pytest_addoption(parser):
    group = parser.getgroup("arcomm", "Arcomm testing options")
    group.addoption("--host", metavar="HOST", action="append",
                    help="Host to use for testing")
    group.addoption("--username", metavar="USERNAME", default="admin",
                    help="Specifies username on host")
    group.addoption("--password", metavar="PASSWORD", default="",
                    help="Specifies password")
    group.addoption("--authorize-password",
                    help=("rescan output directory and regenerate html"
                         "reports, but don't run any test cases"))

@pytest.fixture(scope="session")
def hosts(request):
    """Host hostname or IP address"""
    return request.config.getoption("--host")

@pytest.fixture(scope="session")
def host(request, hosts):
    """Host hostname or IP address"""
    return hosts[0]

@pytest.fixture(scope="session")
def password(request):
    """Username on host"""
    return request.config.getoption("--password")

@pytest.fixture(scope="session")
def username(request):
    """Password for user on host"""
    return request.config.getoption("--username")

@pytest.fixture(scope="session")
def authorize_password(request):
    """Enable secret used to gain privileged access"""
    return request.config.getoption("--authorize-password")

@pytest.fixture(scope="session")
def creds(request):
    """Return a credentials object, used with connect"""
    username = request.config.getoption("--username")
    password = request.config.getoption("--password")
    authorize_password = request.config.getoption("--authorize-password")
    return arcomm.get_credentials(username=username, password=password,
                 authorize_password=authorize_password)

@pytest.fixture(scope="session")
def readonly_creds():
    username, password = READONLY_CREDS
    return arcomm.get_credentials(username=username, password=password)

@pytest.fixture(scope="module", params=PROTOCOLS)
def connection(host, creds, request):
    return arcomm.connect(host, creds, protocol=request.param)


@pytest.fixture(scope="session")
def exec_commands():
    return ["show version", "show clock"]

@pytest.fixture(scope="session")
def configure_commands():
    return ["ip host dummy 127.0.0.1", "ping dummy", "no ip host dummy"]
