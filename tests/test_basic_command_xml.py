#!/usr/bin/env python
"""Tests for `broadworks_ocip` package."""
import pytest  # noqa: F401
from lxml import etree

from broadworks_ocip import BroadworksAPI

BASIC_API_PARAMS = {
    "host": "localhost",
    "username": "username@example.com",
    "password": "password",
    "session": "00000000-1111-2222-3333-444444444444",
}


def canon_xml(inxml):
    """
    we XML canonicalise/pretty print this to prevent whitespace/quote ordering
    issues and to make any diffs easier to read.
    Returned XML is as a decoded string - prettier for diffs
    """
    return etree.tostring(etree.fromstring(inxml), pretty_print=True).decode()


def compare_command_xml(wanted, command, **kwargs):
    """Create a Broadworks XML command framgment from the argumenta"""
    api = BroadworksAPI(**BASIC_API_PARAMS)
    generated = api.get_command_xml(command, **kwargs)
    assert canon_xml(generated) == canon_xml(wanted)


def test_command_xml():
    compare_command_xml(
        (
            b'<?xml version="1.0" encoding="ISO-8859-1"?>\n'
            b'<BroadsoftDocument protocol="OCI" xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            b'<sessionId xmlns="">00000000-1111-2222-3333-444444444444</sessionId>'
            b'<command xmlns="" xsi:type="AuthenticationRequest">'
            b"<userId>username@example.com</userId></command></BroadsoftDocument>"
        ),
        "AuthenticationRequest",
        user_id="username@example.com",
    )


# end
