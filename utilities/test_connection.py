#!/usr/bin/env python
import argparse
import logging

from broadworks_ocip import BroadworksAPI

logging.basicConfig(level=logging.DEBUG, filename="debug.log")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Parse Broadworks OCI-P schema, build interface code",
    )
    parser.add_argument("--host", type=str, required=True)
    parser.add_argument("--port", type=int, default=2208)
    parser.add_argument("--username", type=str, required=True)
    parser.add_argument("--password", type=str, required=True)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    api = BroadworksAPI(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        logger=logger,
    )
    if args.list:
        result = api.command("ServiceProviderGetListRequest")
        for thing in result.service_provider_table:
            print(thing)
    else:
        result = api.command("SystemSoftwareVersionGetRequest")
        print(result)


if __name__ == "__main__":
    main()
