#!/usr/bin/env python
"""Tests for `broadworks_ocip` package."""
import pytest  # noqa: F401

from broadworks_ocip import BroadworksAPI

BASIC_API_PARAMS = {
    "host": "localhost",
    "username": "username@example.com",
    "password": "password",
    "session": "00000000-1111-2222-3333-444444444444",
}


def command_xml(command, **kwargs):
    """Create a Broadworks XML command framgment from the argumenta"""
    api = BroadworksAPI(**BASIC_API_PARAMS)
    return api.get_command_xml(command, **kwargs)


def test_command_xml():
    assert command_xml("AuthenticationRequest", user_id="username@example.com") == (
        b"<?xml version='1.0' encoding='ISO-8859-1'?>\n<BroadsoftDocument "
        b'xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" protocol="OCI">'
        b'<sessionId xmlns="">00000000-1111-2222-3333-444444444444</sessionId>'
        b'<command xmlns="" xsi:type="AuthenticationRequest"><userId>username@example.com</userId>'
        b"</command></BroadsoftDocument>"
    )
