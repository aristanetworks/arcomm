import arcomm.async
import time
import pytest
# def test_background():
#     creds = arcomm.get_credentials(username="admin", password="",
#                                   authorize_password="s3cr3t")
#     command = "bash sleep 2"
#     with arcomm.async.Background("spine2a", creds=creds, commands=command,
#                                  protocol="ssh") as bg:
#         pass
#
#     assert bg.results.closed, "Queue did not close correctly"

@pytest.mark.parametrize("protocol,encoding", [
    ("ssh", "text"),
    ("ssh", "json"),
    ("eapi", "text"),
    ("eapi", "json")
])
def test_pool_with(creds, host, protocol, encoding):
    commands = ["show version", "show clock"]
    with arcomm.async.Pool([host], creds=creds, commands=commands,
                           protocol=protocol, encoding=encoding) as pool:
        time.sleep(1)
    
    for result in pool.results:
        assert "response" in result, "No response in result"