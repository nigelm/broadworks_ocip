#!/usr/bin/env python
import argparse

from broadworks_ocip.api import BroadoworksAPI


def main():
    parser = argparse.ArgumentParser(
        description="Parse Broadworks OCI-P schema, build interface code",
    )
    parser.add_argument("--host", type=str, required=True)
    parser.add_argument("--port", type=int, default=2208)
    parser.add_argument("--username", type=str, required=True)
    parser.add_argument("--password", type=str, required=True)
    args = parser.parse_args()

    api = BroadoworksAPI(
        host=args.host, port=args.port, username=args.username, password=args.password,
    )
    result = api.command("ServiceProviderGetListRequest")
    for thing in result.service_provider_table:
        print(thing)


if __name__ == "__main__":
    main()
