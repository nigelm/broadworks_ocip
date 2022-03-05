#!/usr/bin/env python
from broadworks_ocip import BroadworksAPI

api = BroadworksAPI(
    host="localhost",
    username="username@example.com",
    password="password",
    session_id="00000000-1111-2222-3333-444444444444",
)


def test_default_session_id():
    xml = (
        b'<?xml version="1.0" encoding="ISO-8859-1"?>\n'
        b'<BroadsoftDocument protocol="OCI" xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        b'<sessionId xmlns="">00000000-1111-2222-3333-444444444444</sessionId>'
        b'<command echo="" xsi:type="SystemSoftwareVersionGetResponse" xmlns="">'
        b"<version>24</version>"
        b"</command>"
        b"</BroadsoftDocument>\n"
    )
    decoded = api.decode_xml(xml)
    assert decoded.type_ == "SystemSoftwareVersionGetResponse"
    assert decoded.version == "24"
    assert decoded.session_id == "00000000-1111-2222-3333-444444444444"


def test_real_session_id():
    xml = (
        b'<?xml version="1.0" encoding="ISO-8859-1"?>\n'
        b'<BroadsoftDocument protocol="OCI" xmlns="C" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        b'<sessionId xmlns="">770f845b-2caf-44bc-9291-e9eac7afaaf4</sessionId>'
        b'<command echo="" xsi:type="SystemSoftwareVersionGetResponse" xmlns="">'
        b"<version>24</version>"
        b"</command>"
        b"</BroadsoftDocument>\n"
    )
    decoded = api.decode_xml(xml)
    assert decoded.type_ == "SystemSoftwareVersionGetResponse"
    assert decoded.version == "24"
    assert decoded.session_id == "770f845b-2caf-44bc-9291-e9eac7afaaf4"
