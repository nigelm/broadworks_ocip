# This code is based on https://medium.com/@hmajid2301/pytest-with-background-thread-fixtures-f0dc34ee3c46
import logging
import select
import socket
import sys

from broadworks_ocip import BroadworksAPI

FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s",
)

BASIC_API_PARAMS = {
    "host": "localhost",
    "username": "username@example.com",
    "password": "password",
    "session_id": "00000000-1111-2222-3333-444444444444",
}


class FakeServer:
    def __init__(self, port=0):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.configure_logger()
        self.logger.debug("Instantiated FakeServer")

    def __enter__(self):
        self.socket.bind(("127.0.0.1", self.port))
        host, port = self.socket.getsockname()
        self.logger.debug(f"Listening on tcp://{host}:{port}")
        self.port = port
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            # this seems to happen...
            pass
        self.socket.close()
        self.logger.info(f"Disconnected socket port={self.port}")

    def listen_for_traffic(self):
        while True:
            self.socket.listen(5)
            connection, address = self.socket.accept()
            (host, port) = address
            self.logger.info(f"Connection from host={host} port={port}")
            api = BroadworksAPI(**BASIC_API_PARAMS, logger=self.logger)

            while True:
                content = b""
                while True:
                    readable, writable, exceptional = select.select(
                        [connection],
                        [],
                        [connection],
                        5,
                    )
                    if readable:  # there is only one thing in the set...
                        try:
                            content += connection.recv(4096)
                        except ConnectionResetError:
                            self.logger.debug("Connection got reset")
                            connection.close()
                            return
                        # look for the end of document marker (we ignore line ends)
                        splits = content.partition(b"</BroadsoftDocument>")
                        if len(splits[1]) > 0:
                            break
                    elif exceptional:
                        self.logger.debug("Connection likely terminated")
                        connection.close()
                        return
                    elif not readable and not writable and not exceptional:
                        self.logger.debug("Read timeout")
                        connection.close()
                        return
                self.logger.debug(f"RECV: {str(content)}")
                self.process_command(connection, content, api)

    def configure_logger(self):
        """ """
        logger = logging.getLogger("fake_server")
        logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(FORMATTER)
        logger.addHandler(console_handler)
        self.logger = logger

    def process_command(self, connection, content, api):
        cmd = api.decode_xml(content)
        self.logger.debug(f"F<<<: {cmd.type_}")
        response = None
        if cmd.type_ == "AuthenticationRequest":
            response = api.get_command_object(
                "AuthenticationResponse",
                user_id=cmd.user_id,
                nonce="1234567890123",
                password_algorithm="MD5",
            )
        elif cmd.type_ == "LoginRequest14sp4":
            # hard coded password corresponding to the hard coded params at top
            if cmd.signed_password == "77e4a6de3a1e00be05e121cf0ebee860":
                domain = cmd.user_id.partition("@")[2]
                if domain == "":
                    domain = "example.org"
                response = api.get_command_object(
                    "LoginResponse14sp4",
                    login_type="System",
                    locale="en_GB",
                    encoding="ISO-8859",
                    is_enterprise=False,
                    user_domain=domain,
                )
            else:
                response = api.get_command_object(
                    "ErrorResponse",
                    summary="[Error 4962] Invalid password",
                    summary_english="[Error 4962] Invalid password",
                )
        elif cmd.type_ == "SystemSoftwareVersionGetRequest":
            response = api.get_command_object(
                "SystemSoftwareVersionGetResponse",
                version="21sp1",
            )
        elif cmd.type_ == "LogoutRequest":
            # This normally never gets sent because the other end drops the connection
            response = api.get_command_object("SuccessResponse")
        else:
            response = api.get_command_object(
                "ErrorResponse",
                error_code=9999,
                summary="Server is a fake and a fraud",
                summary_english="This is not a real server and doesn't implement many things",
                detail="There might be more detail if this was a real server",
                type="abject_panic",
            )
        self.logger.debug(f"Built response {response.type_}")
        xml = response.build_xml_()
        self.logger.debug(f"F>>>: {response.type_}")
        connection.sendall(xml + b"\n")
        self.logger.debug(f"SEND: {str(xml)}")
