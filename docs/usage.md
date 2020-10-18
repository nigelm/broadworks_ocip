# Usage

## Simple Usage

To use Broadworks OCI-P Interface in a project:-

```python
    from broadworks_ocip import BroadworksAPI

    # configure the API, connect and authenticate to the server
    api = BroadworksAPI(
        host=args.host, port=args.port, username=args.username, password=args.password,
    )

    # get the platform software level
    response = api.command("SystemSoftwareVersionGetRequest")
    print(response.version)

    # get a list of Service Providers on the platform
    response = api.command("ServiceProviderGetListRequest")

    # the response table is provided as a list of named tuple entries
    for provider in response.service_provider_table:
        print(provider.service_provider_id)
```


## More Complex Usage

Some commands are more complex and made up of additional type components.
This could lead to commands such as this::

```python
    result = api.get_command_object(
        "GroupServiceModifyAuthorizationListRequest",
        service_provider_id="some_enterprise",
        group_id="somegroup",
        service_pack_authorization=[    # a list of ServicePackAuthorization objects
            api.get_type_object(        # authorized, no limits
                "ServicePackAuthorization",
                service_pack_name="Voicemail",
                authorized_quantity=api.get_type_object(
                    "UnboundedPositiveInt",
                    unlimited=True,
                ),
            ),
            api.get_type_object(        # authorized, limited to 32 instances
                "ServicePackAuthorization",
                service_pack_name="Hushmail",
                authorized_quantity=api.get_type_object(
                    "UnboundedPositiveInt",
                    quantity=32,
                ),
            ),
            api.get_type_object(        # de-authorized
                "ServicePackAuthorization",
                service_pack_name="Phone",
                unauthorized=True,
            ),
        ],
    )
```

## Failures and Exceptions

A failed command typically returns an `ErrorResponse`.  When decoded the
`ErrorResponse` will raise a `OCIErrorResponse` exception.

Additionally a command may raise other exceptions, related to the TCP
communications layers, or a `OCIErrorTimeOut` if no response is received in
reasonable time.

## Server

Due to the way these objects have been built it *should* be fairly simple to
make a Broadworks OCI-P server which accepts and decodes requests and replies
with appropriate responses; and this was done in a very simplified form to
make the `fakeserver.py` which is used in testing.  However this is not likely
to be very useful in practice.
