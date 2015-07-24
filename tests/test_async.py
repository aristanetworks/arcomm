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
    ("ssh", "text"), ("ssh", "json"), ("eapi", "text"), ("eapi", "json")
])
def test_pool_with(creds, hosts, protocol, encoding):
    commands = ["show version", "show clock"]
    with arcomm.async.Pool(hosts, creds=creds, commands=commands,
                           protocol=protocol, encoding=encoding) as pool:
        time.sleep(1)

    for result in pool.results:
        #print result.get("response"), result.get("error")
        assert "response" in result, "No response in result"

def test_pool_slow_command(host, creds, exec_commands):

    pool = arcomm.async.Pool([host] * 4, creds=creds, commands=["bash sleep 30"],
                             protocol="ssh", timeout=60)
    pool.start()
    pool.join()

    for result in pool.results:
        assert "response" in result, "No response in result"
