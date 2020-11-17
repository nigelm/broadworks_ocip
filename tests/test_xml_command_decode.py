#!/usr/bin/env python
"""Tests for `broadworks_ocip` package."""
from collections import namedtuple

import pytest  # noqa: F401

from broadworks_ocip import BroadworksAPI

BASIC_API_PARAMS = {
    "host": "localhost",
    "username": "username@example.com",
    "password": "password",
    "session_id": "00000000-1111-2222-3333-444444444444",
}


class serviceProviderTable(
    namedtuple(
        "serviceProviderTable",
        ["service_provider_id", "service_provider_name", "is_enterprise"],
    ),
):
    pass


def make_command_from_xml(xml, command, serialised):
    """Create a Broadworks XML command framgment from the argumenta"""
    api = BroadworksAPI(**BASIC_API_PARAMS)
    generated = api.decode_xml(xml)
    assert generated.type_ == command
    assert generated.to_dict() == serialised


def test_service_provider_list_xml():
    make_command_from_xml(
        (
            b'<?xml version="1.0" encoding="ISO-8859-1"?>\n'
            b'<BroadsoftDocument protocol="OCI" xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            b'<sessionId xmlns="">00000000-1111-2222-3333-444444444444</sessionId>'
            b'<command echo="" xsi:type="ServiceProviderGetListResponse" xmlns="">'
            b"<serviceProviderTable>"
            b"<colHeading>Service Provider Id</colHeading>"
            b"<colHeading>Service Provider Name</colHeading>"
            b"<colHeading>Is Enterprise</colHeading>"
            b"<row><col>one</col><col/><col>true</col></row>"
            b"<row><col>two</col><col/><col>true</col></row>"
            b"<row><col>three</col><col/><col>true</col></row>"
            b"<row><col>four</col><col/><col>true</col></row>"
            b"<row><col>five</col><col/><col>true</col></row>"
            b"<row><col>six</col><col>six name</col><col>true</col></row>"
            b"<row><col>seven</col><col/><col>true</col></row>"
            b"<row><col>eight</col><col/><col>true</col></row>"
            b"<row><col>nine</col><col/><col>true</col></row>"
            b"<row><col>ten</col><col>ten name</col><col>true</col></row>"
            b"<row><col>eleven</col><col/><col>true</col></row>"
            b"</serviceProviderTable>"
            b"</command>"
            b"</BroadsoftDocument>\n"
        ),
        "ServiceProviderGetListResponse",
        {
            "session_id": "00000000-1111-2222-3333-444444444444",
            "service_provider_table": [
                serviceProviderTable(
                    service_provider_id="one",
                    service_provider_name=None,
                    is_enterprise="true",
                ),
                serviceProviderTable(
                    service_provider_id="two",
                    service_provider_name=None,
                    is_enterprise="true",
                ),
                serviceProviderTable(
                    service_provider_id="three",
                    service_provider_name=None,
                    is_enterprise="true",
                ),
                serviceProviderTable(
                    service_provider_id="four",
                    service_provider_name=None,
                    is_enterprise="true",
                ),
                serviceProviderTable(
                    service_provider_id="five",
                    service_provider_name=None,
                    is_enterprise="true",
                ),
                serviceProviderTable(
                    service_provider_id="six",
                    service_provider_name="six name",
                    is_enterprise="true",
                ),
                serviceProviderTable(
                    service_provider_id="seven",
                    service_provider_name=None,
                    is_enterprise="true",
                ),
                serviceProviderTable(
                    service_provider_id="eight",
                    service_provider_name=None,
                    is_enterprise="true",
                ),
                serviceProviderTable(
                    service_provider_id="nine",
                    service_provider_name=None,
                    is_enterprise="true",
                ),
                serviceProviderTable(
                    service_provider_id="ten",
                    service_provider_name="ten name",
                    is_enterprise="true",
                ),
                serviceProviderTable(
                    service_provider_id="eleven",
                    service_provider_name=None,
                    is_enterprise="true",
                ),
            ],
        },
    )


def test_service_pack_list_xml():
    make_command_from_xml(
        (
            b'<?xml version="1.0" encoding="ISO-8859-1"?>\n'
            b'<BroadsoftDocument protocol="OCI" xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            b'<sessionId xmlns="">00000000-1111-2222-3333-444444444444</sessionId>'
            b'<command echo="" xsi:type="ServiceProviderServicePackGetListResponse" xmlns="">'
            b"<servicePackName>Pack_1</servicePackName>"
            b"<servicePackName>Pack_2</servicePackName>"
            b"<servicePackName>Pack_3</servicePackName>"
            b"<servicePackName>Pack_4</servicePackName>"
            b"<servicePackName>Pack_5</servicePackName>"
            b"<servicePackName>Pack_6</servicePackName>"
            b"<servicePackName>Pack_7</servicePackName>"
            b"<servicePackName>Pack_8</servicePackName>"
            b"</command>"
            b"</BroadsoftDocument>\n"
        ),
        "ServiceProviderServicePackGetListResponse",
        {
            "session_id": "00000000-1111-2222-3333-444444444444",
            "service_pack_name": [
                "Pack_1",
                "Pack_2",
                "Pack_3",
                "Pack_4",
                "Pack_5",
                "Pack_6",
                "Pack_7",
                "Pack_8",
            ],
        },
    )


# end
