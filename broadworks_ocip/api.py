"""
Broadworks OCI-P Interface API Class and code

Main API interface - this is basically the only consumer visible part
"""
import hashlib
import inspect
import logging
import select
import socket
import sys
import uuid

from classforge import Class
from classforge import Field
from lxml import etree

import broadworks_ocip.base
import broadworks_ocip.requests
import broadworks_ocip.responses
import broadworks_ocip.types
from broadworks_ocip.exceptions import OCIErrorTimeOut
from broadworks_ocip.exceptions import OCIErrorUnknown

VERBOSE_DEBUG = 9


class BroadworksAPI(Class):
    """
    BroadworksAPI - A class encapsulating the Broadworks OCI-P API

    This encapsulates a connection to the Broadworks OCI-P API server and
    provides an interface to cerate and despatch commands to the server and
    receive responses back (as response class instances).

    Attributes:
        host: hostname/ip to connect to
        port: port number to connect to. Default 2208
        username: username to authenticate with
        password: password to authenticate with
        logger: logger object to use - set up internally by default
        authenticated: are we authenticated?
        connect_timeout: connection timeout value (default 8)
        command_timeout: command timeout value (default 30)
        socket: connection socket - set up internally
        session_id: session id - set up internally, only set this for testing

    """

    host: str = Field(type=str, required=True, mutable=False)
    port: int = Field(type=int, default=2208, mutable=False)
    username: str = Field(type=str, required=True, mutable=False)
    password: str = Field(type=str, required=True, mutable=False)
    logger = Field(type=logging.Logger)
    authenticated: bool = Field(type=bool, default=False)
    connect_timeout: int = Field(type=int, default=8)
    command_timeout: int = Field(type=int, default=30)
    socket = Field(type=socket.socket, default=None)  # type: socket.socket
    session_id: str = Field(type=str)
    _despatch_table = Field(type=dict)

    def on_init(self):
        """
        Initialise the API object.

        Automatically called by the object initialisation code. Sets up the
        session_id to a random `uuid.uuid4()`, builds a logger object if none
        was passed and builds a despatch table.
        """
        if self.session_id is None:
            self.session_id = str(uuid.uuid4())
        if self.logger is None:
            self.configure_logger()
        self.build_despatch_table()
        self.authenticated = False

    def build_despatch_table(self):
        """
        Create a despatch table of commands and types used
        """
        self.logger.debug("Building Broadworks despatch table")
        despatch_table = {}
        # deal with all the main request/responses
        for module in (
            broadworks_ocip.responses,
            broadworks_ocip.requests,
            broadworks_ocip.types,
        ):
            for name, data in inspect.getmembers(module, inspect.isclass):
                if name.startswith("__"):
                    continue
                try:
                    if data.__module__ in (
                        "broadworks_ocip.types",
                        "broadworks_ocip.requests",
                        "broadworks_ocip.responses",
                    ):
                        despatch_table[name] = data
                except AttributeError:
                    continue
        # deal with special cases in base
        for name, data in inspect.getmembers(broadworks_ocip.base, inspect.isclass):
            if name in ("SuccessResponse", "ErrorResponse"):
                despatch_table[name] = data
                despatch_table["c:" + name] = data  # namespace issues
        # we now have a despatch table...
        self._despatch_table = despatch_table
        self.logger.debug("Built Broadworks despatch table")

    def configure_logger(self):
        """
        Create and configure a logging object

        By default sets up a basic logger logging to the console and syslog at
        `WARNING` level.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.WARNING)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        logger.addHandler(console_handler)
        self.logger = logger

    def get_type_class(self, command: str):
        """
        Given a name (Request/Response/Type) name, return a class object for it

        Arguments:
            command: A single word name of a OCIType(),OCIRequest(),OCIResponse()

        Raises:
            KeyError: If command could not be found

        Returns:
            cls: An appropriate class object
        """
        try:
            cls = self._despatch_table[command]
        except KeyError as e:
            self.logger.error(f"Unknown command requested - {command}")
            raise e
        return cls

    def get_type_object(self, command, **kwargs):
        """
        Build the OCIType object instance for a type and parameters

        The difference between this method, and `get_command_object()` is that
        the latter set up the session_id (which is only relevant for a command
        object).

        Arguments:
            command: A single word name of a `OCIType()`
            kwargs: The arguments for the type

        Raises:
            KeyError: If command could not be found

        Returns:
            cmd: An appropriate class instance
        """
        cls = self.get_type_class(command)
        cmd = cls(**kwargs)
        return cmd

    def get_command_object(self, command, **kwargs):
        """
        Build the OCICommand object instance for a command and parameter

        The difference between `get_type_object`, and this method is that this
        one sets up the session_id (which is only relevant for a command
        object).

        Arguments:
            command: A single word name of a `OCIRequest()` or `OCIResponse()`
            kwargs: The arguments for the command

        Raises:
            KeyError: If command could not be found

        Returns:
            cmd: An appropriate class instance
        """
        cls = self.get_type_class(command)
        cmd = cls(session_id=self.session_id, **kwargs)
        return cmd

    def get_command_xml(self, command, **kwargs):
        """
        Build the XML for a command and parameter

        Arguments:
            command: A single word name of a `OCIRequest()` or `OCIResponse()`
            kwargs: The arguments for the command

        Raises:
            KeyError: If command could not be found

        Returns:
            xml: An XML string
        """
        cmd = self.get_command_object(command, **kwargs)
        return cmd.build_xml_()

    def send_command(self, command, **kwargs):
        """
        Build the XML for a command and parameter and send it to the server

        Arguments:
            command: A single word name of a `OCIRequest()` or `OCIResponse()`
            kwargs: The arguments for the command

        Raises:
            KeyError: If command could not be found

        Returns:
            None
        """
        self.logger.info(f">>> {command}")
        xml = self.get_command_xml(command, **kwargs)
        self.logger.log(VERBOSE_DEBUG, f"SEND: {str(xml)}")
        self.socket.sendall(xml + b"\n")

    def receive_response(self):
        """
        Wait and receive response XML from server, and decode it

        Arguments:

        Raises:
            OCIErrorResponse: An error was returned from the server
            OCIErrorTimeOut: The client timed out waiting for the server
            OCIErrorUnknown: Unknown return from the server
            IOError: Communications failure

        Returns:
            Class instance object
        """
        content = b""
        while True:
            readable, writable, exceptional = select.select(
                [self.socket],
                [],
                [],
                self.command_timeout,
            )
            if readable:  # there is only one thing in the set...
                content += self.socket.recv(4096)
                # look for the end of document marker (we ignore line ends)
                splits = content.partition(b"</BroadsoftDocument>")
                if len(splits[1]) > 0:
                    break
            elif not readable and not writable and not exceptional:
                raise OCIErrorTimeOut(object=self, message="Read timeout")
        self.logger.log(VERBOSE_DEBUG, f"RECV: {str(content)}")
        return self.decode_xml(content)

    def decode_xml(self, xml):
        """
        Decode XML into an OCICommand based object instance

        Arguments:
            xml: An XML string

        Raises:
            OCIErrorResponse: An error was returned from the server
            OCIErrorUnknown: Unknown return from the server

        Returns:
            Class instance object
        """
        root = etree.fromstring(xml)
        if root.tag != "{C}BroadsoftDocument":
            raise ValueError
        self.logger.debug("Decoding BroadsoftDocument")
        for element in root:
            if element.tag == "command":
                command = element.get("{http://www.w3.org/2001/XMLSchema-instance}type")
                self.logger.debug(f"Decoding command {command}")
                cls = self._despatch_table[command]
                result = cls.build_from_etree_(element)
                self.logger.info(f"<<< {result.type_}")
                result.post_xml_decode_()
                return result
        raise OCIErrorUnknown(message="Unknown XML decode", object=root)

    def connect(self):
        """
        Open the connection to the OCI-P server

        Arguments:

        Raises:
            IOError: Communications failure

        Returns:
            None
        """
        self.logger.debug(f"Attempting connection host={self.host} port={self.port}")
        try:
            address = (self.host, self.port)
            conn = socket.create_connection(
                address=address,
                timeout=self.connect_timeout,
            )
            self.socket = conn
            self.logger.info(f"Connected to host={self.host} port={self.port}")
        except OSError as e:
            self.logger.error("Connection failed")
            raise e
        except socket.timeout as e:
            self.logger.error("Connection timed out")
            raise e

    def authenticate(self):
        """
        Authenticate the connection to the OCI-P server

        Arguments:

        Raises:
            OCIErrorResponse: An error was returned from the server

        Returns:
            resp: Response object
        """
        self.send_command("AuthenticationRequest", user_id=self.username)
        resp = self.receive_response()
        authhash = hashlib.sha1(self.password.encode()).hexdigest().lower()
        signed_password = (
            hashlib.md5(":".join([resp.nonce, authhash]).encode()).hexdigest().lower()
        )
        self.send_command(
            "LoginRequest14sp4",
            user_id=self.username,
            signed_password=signed_password,
        )
        # if this fails to authenticate an ErrorResponse will be returned which forces
        # an exception to be raised
        resp = self.receive_response()
        # if authentication failed this line will never be executed
        self.authenticated = True
        return resp

    def command(self, command, **kwargs):
        """
        Send a command and parameters to the server, receive and decode a response

        Arguments:
            command: A single word name of a `OCIRequest()`
            kwargs: The arguments for the command

        Raises:
            OCIErrorResponse: An error was returned from the server
            OCIErrorTimeOut: The client timed out waiting for the server
            OCIErrorUnknown: Unknown return from the server
            IOError: Communications failure

        Returns:
            resp: Response class instance object
        """
        if not self.authenticated:
            self.connect()
            self.authenticate()
        self.send_command(command, **kwargs)
        return self.receive_response()

    def close(self, no_log=False):
        """
        Close the connection to the OCI-P server
        """
        if self.authenticated and not no_log:
            self.logger.debug("Disconnect by logging out")
            self.send_command(
                "LogoutRequest",
                user_id=self.username,
                reason="Connection close",
            )
            self.authenticated = False
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except OSError:
                pass  # we just ignore this under these circumstances
            if not no_log:
                self.logger.info(f"Disconnected from host={self.host} port={self.port}")
            self.socket = None

    def __del__(self):
        self.close(no_log=True)


# end
