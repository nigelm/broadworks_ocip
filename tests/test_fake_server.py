#!/usr/bin/env python
# This code is based on https://medium.com/@hmajid2301/pytest-with-background-thread-fixtures-f0dc34ee3c46
"""Tests for `broadworks_ocip` package."""
import threading

import pytest  # noqa: F401

from broadworks_ocip import BroadworksAPI
from broadworks_ocip import OCIErrorResponse
from tests.fakeserver import FakeServer

SERVER_TCP_PORT = 2208
BASIC_API_PARAMS = {
    "host": "127.0.0.1",
    "port": SERVER_TCP_PORT,
    "username": "username@example.com",
    "password": "password",
    "session_id": "00000000-1111-2222-3333-444444444444",
    "connect_timeout": 3,
}


@pytest.fixture(autouse=True)
def dummy_tcp_server():
    tcp_server = FakeServer(port=SERVER_TCP_PORT)
    with tcp_server as example_server:
        thread = threading.Thread(target=example_server.listen_for_traffic)
        thread.daemon = True
        thread.start()
        yield example_server


def test_server_login():
    api = BroadworksAPI(**BASIC_API_PARAMS)
    assert api is not None
    assert api.__class__.__name__ == "BroadworksAPI"
    assert api.authenticated is False
    response = api.command("SystemSoftwareVersionGetRequest")
    assert api.authenticated is True
    assert response is not None
    assert response.type_ == "SystemSoftwareVersionGetResponse"


def test_server_login_fail():
    params = BASIC_API_PARAMS
    params["password"] = "wrong wrong wrong"
    api = BroadworksAPI(**params)
    assert api is not None
    assert api.__class__.__name__ == "BroadworksAPI"
    assert api.authenticated is False
    with pytest.raises(OCIErrorResponse) as excinfo:
        api.command("SystemSoftwareVersionGetRequest")
    assert "Invalid password" in str(excinfo.value)
    assert api.authenticated is False


# end
