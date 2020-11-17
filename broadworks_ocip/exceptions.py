"""
Broadworks OCI-P Interface Exception Classes

Exception classes used by the API.
"""
import attr


@attr.s(slots=True, frozen=True)
class OCIError(Exception):
    """Base Exception raised by OCI operations.

    Attributes:
        message: explanation of why it went bang
        object: the thing that went bang
    """

    message: str = attr.ib()
    object = attr.ib(default=None)

    def __str__(self):
        return f"{self.__class__.__name__}({self.message})"


class OCIErrorResponse(OCIError):
    """
    Exception raised when an ErrorResponse is received and decoded.

    Subclass of OCIError()
    """

    pass


class OCIErrorTimeOut(OCIError):
    """
    Exception raised when nothing is head back from the server.

    Subclass of OCIError()
    """

    pass


class OCIErrorUnknown(OCIError):
    """
    Exception raised when life becomes too much for the software.

    Subclass of OCIError()
    """

    pass


# end
