# Broadworks OCI-P Interface


[![ci](https://img.shields.io/travis/com/nigelm/broadworks_ocip.svg)](https://travis-ci.com/nigelm/broadworks_ocip)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://nigelm.github.io/broadworks_ocip/)
[![pypi version](https://img.shields.io/pypi/v/broadworks_ocip.svg)](https://pypi.python.org/pypi/broadworks_ocip)

`broadworks_ocip` interfaces to the OCI-P provisioning interface of a Broadworks softswitch


- Free software: BSD license
- Documentation: https://nigelm.github.io/broadworks_ocip/

----

## Features

- python objects to match all Broadworks schema objects
- API framework to talk to a Broadworks server
- additional magic to handle authentication and sessions
- Based on Broadworks schema R21

## Current Version

Version: `1.4.0`

----

## Installation

With `pip`:
```bash
python3 -m pip install broadworks-ocip
```

----

## Usage

More details is given within the usage section of the documentation, but the
minimal summary is:-

```python
from broadworks_ocip import BroadworksAPI

# configure the API, connect and authenticate to the server
api = BroadworksAPI(
    host=args.host, port=args.port, username=args.username, password=args.password,
)

# get the platform software level
response = api.command("SystemSoftwareVersionGetRequest")
print(response.version)
```

## Credits

The class is built using Michael DeHaan's [`ClassForge`](https://classforge.io/) object system.

Development on the python version was done by
[Nigel Metheringham `<nigelm@cpan.org>`](https://github.com/nigelm/)

Karol Skibiński has been using the package, and has a talent for both finding
bugs within it and providing a good bug report that allows a test case and fix
to be made.  The package has been immensely improved by this work.

----
