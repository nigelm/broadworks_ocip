#!/usr/bin/env python
"""Tests for `broadworks_ocip` package."""
import threading

import pytest  # noqa: F401

from broadworks_ocip import BroadworksAPI
from tests.fakeserver import FakeServer

SERVER_TCP_PORT = 2208
BASIC_API_PARAMS = {
    "host": "127.0.0.1",
    "port": SERVER_TCP_PORT,
    "username": "username@example.com",
    "password": "password",
    "session": "00000000-1111-2222-3333-444444444444",
    "timeout": 20,
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
    response = api.command("SystemSoftwareVersionGetRequest")
    assert response is not None


# end
