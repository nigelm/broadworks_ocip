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


def test_service_provider_service_pack_get_detail_list_response_xml():
    userServiceTable = namedtuple(
        "userServiceTable",
        ["service", "authorized", "allocated", "available"],
    )
    make_command_from_xml(
        (
            b'<?xml version="1.0" encoding="ISO-8859-1"?>\n'
            b'<BroadsoftDocument protocol="OCI" xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            b'<sessionId xmlns="">00000000-1111-2222-3333-444444444444</sessionId>'
            b'<command echo="" xsi:type="ServiceProviderServicePackGetDetailListResponse" xmlns="">'
            b"<servicePackName>Service-Pack-Standard</servicePackName>"
            b"<servicePackDescription>Service Pack - Standard</servicePackDescription>"
            b"<isAvailableForUse>true</isAvailableForUse>"
            b"<servicePackQuantity><unlimited>true</unlimited></servicePackQuantity>"
            b"<assignedQuantity><unlimited>true</unlimited></assignedQuantity>"
            b"<allowedQuantity><unlimited>true</unlimited></allowedQuantity>"
            b"<userServiceTable>"
            b"<colHeading>Service</colHeading>"
            b"<colHeading>Authorized</colHeading>"
            b"<colHeading>Allocated</colHeading>"
            b"<colHeading>Available</colHeading>"
            b"<row>"
            b"<col>Call Center - Standard</col>"
            b"<col>Unlimited</col>"
            b"<col>Unlimited</col>"
            b"<col>Unlimited</col>"
            b"</row>"
            b"</userServiceTable>"
            b"</command></BroadsoftDocument>"
        ),
        "ServiceProviderServicePackGetDetailListResponse",
        {
            "session_id": "00000000-1111-2222-3333-444444444444",
            "allowed_quantity": {"quantity": None, "unlimited": True},
            "assigned_quantity": {"quantity": None, "unlimited": True},
            "is_available_for_use": True,
            "service_pack_description": "Service Pack - Standard",
            "service_pack_name": "Service-Pack-Standard",
            "service_pack_quantity": {"quantity": None, "unlimited": True},
            "user_service_table": [
                userServiceTable(
                    service="Call Center - Standard",
                    authorized="Unlimited",
                    allocated="Unlimited",
                    available="Unlimited",
                ),
            ],
        },
    )


def test_user_call_forwarding_always_get_response():
    make_command_from_xml(
        (
            b'<?xml version="1.0" encoding="ISO-8859-2"?>'
            b'<BroadsoftDocument protocol="OCI" xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            b'<sessionId xmlns="">00000000-1111-2222-3333-444444444444</sessionId>'
            b'<command echo="" xsi:type="UserCallForwardingAlwaysGetResponse" xmlns="">'
            b"<isActive>false</isActive>"
            b"<forwardToPhoneNumber>1234567890</forwardToPhoneNumber>"
            b"<isRingSplashActive>true</isRingSplashActive>"
            b"</command>"
            b"</BroadsoftDocument>"
        ),
        "UserCallForwardingAlwaysGetResponse",
        {
            "session_id": "00000000-1111-2222-3333-444444444444",
            "is_active": False,
            "forward_to_phone_number": "1234567890",
            "is_ring_splash_active": True,
        },
    )


def test_user_assigned_services_get_list_response():
    # Unfortunately I can't use the basic function for this due to differing object locations
    xml = (
        b'<?xml version="1.0" encoding="ISO-8859-2"?>'
        b'<BroadsoftDocument protocol="OCI" xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        b'<sessionId xmlns="">00000000-1111-2222-3333-444444444444</sessionId>'
        b'<command echo="" xsi:type="UserAssignedServicesGetListResponse" xmlns="">'
        b"<groupServiceEntry>"
        b"<serviceName>Music On Hold</serviceName>"
        b"<isActive>true</isActive>"
        b"</groupServiceEntry>"
        b"<userServiceEntry>"
        b"<serviceName>Anonymous Call Rejection</serviceName>"
        b"<isActive>false</isActive>"
        b"</userServiceEntry>"
        b"<userServiceEntry>"
        b"<serviceName>Three-Way Call</serviceName>"
        b"<isActive>true</isActive>"
        b"</userServiceEntry>"
        b"</command>"
        b"</BroadsoftDocument>"
    )

    api = BroadworksAPI(**BASIC_API_PARAMS)
    generated = api.decode_xml(xml)
    assert generated.type_ == "UserAssignedServicesGetListResponse"

    assert (
        generated.group_service_entry[0].to_dict()
        == api.get_type_object(  # noqa: W503
            "AssignedGroupServicesEntry",
            service_name="Music On Hold",
            is_active=True,
        ).to_dict()
    )

    assert (
        generated.user_service_entry[0].to_dict()
        == api.get_type_object(  # noqa: W503
            "AssignedUserServicesEntry",
            service_name="Anonymous Call Rejection",
            is_active=False,
        ).to_dict()
    )

    assert (
        generated.user_service_entry[1].to_dict()
        == api.get_type_object(  # noqa: W503
            "AssignedUserServicesEntry",
            service_name="Three-Way Call",
            is_active=True,
        ).to_dict()
    )


# end
