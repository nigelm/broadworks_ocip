"""Top-level package for Broadworks OCI-P Interface."""
from .api import BroadworksAPI  # noqa: F401
from .exceptions import OCIErrorResponse  # noqa: F401
from .exceptions import OCIErrorTimeOut  # noqa: F401

__author__ = """Nigel Metheringham"""
__email__ = "nigelm@cpan.org"
__version__ = "0.5.1"
