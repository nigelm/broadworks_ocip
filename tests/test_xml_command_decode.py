#!/usr/bin/env python
"""Tests for `broadworks_ocip` package."""
from collections import namedtuple

import pytest  # noqa: F401
from null_object import Null

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


class registrationTable(
    namedtuple(
        "registrationTable",
        [
            "device_level",
            "device_name",
            "order",
            "uri",
            "expiration",
            "line_port",
            "endpoint_type",
            "public_net_address",
            "public_port",
            "private_net_address",
            "private_port",
            "user_agent",
            "lockout_started",
            "lockout_expires",
            "lockout_count",
            "access_info",
            "path_header",
            "registration_active",
        ],
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


def test_group_department_add_xml():
    xml = (
        b'<?xml version="1.0" encoding="ISO-8859-1"?>\n'
        b'<BroadsoftDocument protocol="OCI" xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        b'<sessionId xmlns="">00000000-1111-2222-3333-444444444444</sessionId>'
        b'<command xmlns="" xsi:type="GroupDepartmentAddRequest">'
        b"<serviceProviderId>mysp</serviceProviderId>"
        b"<groupId>mygroup</groupId>"
        b"<departmentName>mydept</departmentName>"
        b'<parentDepartmentKey xsi:type="GroupDepartmentKey">'
        b"<serviceProviderId>mysp</serviceProviderId>"
        b"<groupId>mygroup</groupId>"
        b"<name>test-name</name>"
        b"</parentDepartmentKey>"
        b"<callingLineIdName>clid_name</callingLineIdName>"
        b"</command>"
        b"</BroadsoftDocument>"
    )
    api = BroadworksAPI(**BASIC_API_PARAMS)
    generated = api.decode_xml(xml)
    assert generated.type_ == "GroupDepartmentAddRequest"

    assert (
        generated.parent_department_key.to_dict()
        == api.get_type_object(  # noqa: W503
            "GroupDepartmentKey",
            service_provider_id="mysp",
            group_id="mygroup",
            name="test-name",
        ).to_dict()
    )


def test_nested_elements():
    xml = (
        b'<?xml version="1.0" encoding="ISO-8859-1"?>'
        b'<BroadsoftDocument protocol="OCI" xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        b'<sessionId xmlns="">00000000-1111-2222-3333-444444444444</sessionId>'
        b'<command xsi:type="UserModifyRequest22" xmlns="">'
        b"<userId>user@example.com</userId>"
        b"<phoneNumber>123456789</phoneNumber>"
        b"<extension>1219</extension>"
        b'<sipAliasList xsi:nil="true"/>'
        b"<endpoint>"
        b"<trunkAddressing>"
        b'<trunkGroupDeviceEndpoint xsi:nil="true"/>'
        b"<enterpriseTrunkName>ET02</enterpriseTrunkName>"
        b'<alternateTrunkIdentity xsi:nil="true"/>'
        b"</trunkAddressing>"
        b"</endpoint>"
        b"</command>"
        b"</BroadsoftDocument>"
    )
    api = BroadworksAPI(**BASIC_API_PARAMS)
    generated = api.decode_xml(xml)
    assert generated.type_ == "UserModifyRequest22"
    assert generated.user_id == "user@example.com"
    assert generated.phone_number == "123456789"
    assert generated.sip_alias_list is Null

    # assert generated.sip_alias_list is Null
    print(generated.endpoint["trunk_addressing"])
    assert (
        generated.endpoint["trunk_addressing"].to_dict()
        == api.get_type_object(  # noqa: W503
            "TrunkAddressingMultipleContactModify",
            trunk_group_device_endpoint=Null,
            enterprise_trunk_name="ET02",
            alternate_trunk_identity=Null,
            # physical_location=None,
        ).to_dict()
    )


def test_vpn_policy_decode():
    xml = (
        b'<?xml version="1.0" encoding="ISO-8859-1"?>'
        b'<BroadsoftDocument protocol="OCI" xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        b'<sessionId xmlns="">00000000-1111-2222-3333-444444444444</sessionId>'
        b'<command echo="" xsi:type="EnterpriseVoiceVPNGetPolicyResponse" xmlns="">'
        b"<minExtensionLength>0</minExtensionLength>"
        b"<maxExtensionLength>0</maxExtensionLength>"
        b"<policySelection>Public</policySelection>"
        b'<digitManipulation xsi:type="EnterpriseVoiceVPNDigitManipulationOptionalValue">'
        b"<operation>Prepend</operation>"
        b"<value>253</value>"
        b"</digitManipulation>"
        b"</command>"
        b"</BroadsoftDocument>"
    )
    api = BroadworksAPI(**BASIC_API_PARAMS)
    generated = api.decode_xml(xml)
    assert generated.type_ == "EnterpriseVoiceVPNGetPolicyResponse"
    assert generated.min_extension_length == 0
    assert generated.max_extension_length == 0
    assert generated.description is None
    assert generated.route_group_id is None
    assert generated.policy_selection == "Public"
    assert len(generated.digit_manipulation) == 1
    assert (
        generated.digit_manipulation[0].to_dict()
        == api.get_type_object(  # noqa: W503
            "EnterpriseVoiceVPNDigitManipulationOptionalValue",
            operation="Prepend",
            value="253",
        ).to_dict()
    )
    assert generated.treatment_id is None


def test_unexpected_table_column_name():
    """We did not handle unexpected characters in table column names"""
    xml = (
        b'<?xml version="1.0" encoding="ISO-8859-1"?>'
        b'<BroadsoftDocument protocol="OCI" xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        b'<sessionId xmlns="">00000000-1111-2222-3333-444444444444</sessionId>'
        b'<command echo="" xsi:type="UserGetRegistrationListResponse" xmlns="">'
        b"<registrationTable>"
        b"<colHeading>Device Level</colHeading>"
        b"<colHeading>Device Name</colHeading>"
        b"<colHeading>Order</colHeading>"
        b"<colHeading>URI</colHeading>"
        b"<colHeading>Expiration</colHeading>"
        b"<colHeading>Line/Port</colHeading>"
        b"<colHeading>Endpoint Type</colHeading>"
        b"<colHeading>Public Net Address</colHeading>"
        b"<colHeading>Public Port</colHeading>"
        b"<colHeading>Private Net Address</colHeading>"
        b"<colHeading>Private Port</colHeading>"
        b"<colHeading>User Agent</colHeading>"
        b"<colHeading>Lockout Started</colHeading>"
        b"<colHeading>Lockout Expires</colHeading>"
        b"<colHeading>Lockout Count</colHeading>"
        b"<colHeading>Access Info</colHeading>"
        b"<colHeading>Path Header</colHeading>"
        b"<colHeading>Registration Active</colHeading>"
        b"<row>"
        b"<col>Group</col>"
        b"<col>812345678</col>"
        b"<col>1</col>"
        b"<col>sip:812345678@1.2.3.4:5060;dtg=UC1_BVE_INT_9999_TG;reg-info=39400</col>"
        b"<col>Fri Jul 08 00:01:02 BST 2022</col>"
        b"<col>812345678@voip.hawaiiantel.xxx</col>"
        b"<col>Primary</col>"
        b"<col/>"
        b"<col/>"
        b"<col/>"
        b"<col/>"
        b"<col>PolyEdge-Edge_E220-UA/8.0.0.13670_48256712b942</col>"
        b"<col/>"
        b"<col/>"
        b"<col>0</col>"
        b"<col/>"
        b"<col/>"
        b"<col/>"
        b"</row>"
        b"</registrationTable>"
        b"</command>"
        b"</BroadsoftDocument>"
    )
    api = BroadworksAPI(**BASIC_API_PARAMS)
    generated = api.decode_xml(xml)
    assert generated.type_ == "UserGetRegistrationListResponse"
    assert generated.registration_table == [
        registrationTable(
            device_level="Group",
            device_name="812345678",
            order="1",
            uri="sip:812345678@1.2.3.4:5060;dtg=UC1_BVE_INT_9999_TG;reg-info=39400",
            expiration="Fri Jul 08 00:01:02 BST 2022",
            line_port="812345678@voip.hawaiiantel.xxx",
            endpoint_type="Primary",
            public_net_address=None,
            public_port=None,
            private_net_address=None,
            private_port=None,
            user_agent="PolyEdge-Edge_E220-UA/8.0.0.13670_48256712b942",
            lockout_started=None,
            lockout_expires=None,
            lockout_count="0",
            access_info=None,
            path_header=None,
            registration_active=None,
        ),
    ]


# end
