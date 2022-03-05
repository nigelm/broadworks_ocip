#!/usr/bin/env python
import pytest

from broadworks_ocip import BroadworksAPI
from broadworks_ocip.exceptions import OCIErrorAttributeMissing
from broadworks_ocip.exceptions import OCIErrorUnexpectedAttribute

api = BroadworksAPI(
    host="localhost",
    username="username@example.com",
    password="password",
    session_id="00000000-1111-2222-3333-444444444444",
)


class TestCommandClassConstructor:
    def test_working_base(self):
        cmd = api.get_command_object(
            "GroupAccessDeviceAddRequest14",
            service_provider_id="sp",
            group_id="grp",
            device_name="devname",
            device_type="devtype",
            protocol="SIP 2.0",
            transport_protocol="Unspecified",
            use_custom_user_name_password=True,
            access_device_credentials=api.get_type_object(
                "DeviceManagementUserNamePassword16",
                user_name="tn",
                password="tnpass",
            ),
        )
        assert cmd is not None
        assert "GroupAccessDeviceAddRequest14" in str(type(cmd))

    def test_unexpected_list(self):
        with pytest.raises(TypeError):
            api.get_command_object(
                "GroupAccessDeviceAddRequest14",
                service_provider_id="sp",
                group_id="grp",
                device_name="devname",
                device_type="devtype",
                protocol="SIP 2.0",
                transport_protocol="Unspecified",
                use_custom_user_name_password=True,
                access_device_credentials=[  # this should not be an array
                    api.get_type_object(
                        "DeviceManagementUserNamePassword16",
                        user_name="tn",
                        password="tnpass",
                    ),
                ],
            )

    def test_not_a_bool(self):
        with pytest.raises(TypeError):
            api.get_command_object(
                "GroupAccessDeviceAddRequest14",
                service_provider_id="sp",
                group_id="grp",
                device_name="devname",
                device_type="devtype",
                protocol="SIP 2.0",
                transport_protocol="Unspecified",
                use_custom_user_name_password="true",  # not a bool
                access_device_credentials=api.get_type_object(
                    "DeviceManagementUserNamePassword16",
                    user_name="tn",
                    password="tnpass",
                ),
            )

    def test_unexpected_bool(self):
        with pytest.raises(TypeError):
            api.get_command_object(
                "GroupAccessDeviceAddRequest14",
                service_provider_id="sp",
                group_id="grp",
                device_name="devname",
                device_type="devtype",
                protocol="SIP 2.0",
                transport_protocol=False,  # unexpected bool
                use_custom_user_name_password=True,
                access_device_credentials=api.get_type_object(
                    "DeviceManagementUserNamePassword16",
                    user_name="tn",
                    password="tnpass",
                ),
            )

    def test_too_many_things(self):
        with pytest.raises(TypeError):
            api.get_command_object(
                "GroupAccessDeviceAddRequest14",
                service_provider_id="sp",
                group_id="grp",
                device_name=["devname", "moredevname"],  # so many things
                device_type="devtype",
                protocol="SIP 2.0",
                transport_protocol="Unspecified",
                use_custom_user_name_password=True,
                access_device_credentials=api.get_type_object(
                    "DeviceManagementUserNamePassword16",
                    user_name="tn",
                    password="tnpass",
                ),
            )

    def test_missing_attribute(self):
        cmd = api.get_command_object(
            "GroupAccessDeviceAddRequest14",
            service_provider_id="sp",
            group_id="grp",
            device_name="devname",
            device_type="devtype",
            # protocol="SIP 2.0",   # missing optional attrobute
            transport_protocol="Unspecified",
            use_custom_user_name_password=True,
            access_device_credentials=api.get_type_object(
                "DeviceManagementUserNamePassword16",
                user_name="tn",
                password="tnpass",
            ),
        )
        assert cmd is not None

        with pytest.raises(OCIErrorAttributeMissing):
            api.get_command_object(
                "GroupAccessDeviceAddRequest14",
                # service_provider_id="sp",   # missing required attrobute
                group_id="grp",
                device_name="devname",
                device_type="devtype",
                protocol="SIP 2.0",
                transport_protocol="Unspecified",
                use_custom_user_name_password=True,
                access_device_credentials=api.get_type_object(
                    "DeviceManagementUserNamePassword16",
                    user_name="tn",
                    password="tnpass",
                ),
            )

    def test_extra_attribute(self):
        with pytest.raises(OCIErrorUnexpectedAttribute):
            api.get_command_object(
                "GroupAccessDeviceAddRequest14",
                unexpected_attribute="strange value",
                service_provider_id="sp",
                group_id="grp",
                device_name="devname",
                device_type="devtype",
                protocol="SIP 2.0",
                transport_protocol="Unspecified",
                use_custom_user_name_password=True,
                access_device_credentials=api.get_type_object(
                    "DeviceManagementUserNamePassword16",
                    user_name="tn",
                    password="tnpass",
                ),
            )
