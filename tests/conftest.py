import pytest
#from arcomm import Creds
import arcomm
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

@pytest.fixture(scope="function")
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
