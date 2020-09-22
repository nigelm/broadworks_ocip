"""
Broadworks OCI-P Interface Exception Classes

Exception classes used by the API.
"""


class OCIError(Exception):
    """Base Exception raised by OCI operations.

    Attributes:
        message -- explanation of why it went bang
        object -- the thing that went bang
    """

    def __init__(self, message, object=None):
        self.message = message
        self.object = object

    def __str__(self):
        return f"{self.__class__.__name__}({self.message})"


class OCIErrorResponse(OCIError):
    pass


class OCIErrorTimeOut(OCIError):
    pass


# end
