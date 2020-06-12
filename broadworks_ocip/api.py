import inspect
import logging
import sys
import uuid

from classforge import Class
from classforge import Field
from lxml import etree

import broadworks_ocip.requests
import broadworks_ocip.responses
import broadworks_ocip.types


FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s",
)


class BroadoworksAPI(Class):
    session = Field(type=str)
    host = Field(type=str, required=True)
    port = Field(type=int, required=True)
    username = Field(type=str, required=True)
    password = Field(type=str, required=True)
    logger = Field(type=object)
    despatch_table = Field(type=dict)
    authenticated = Field(type=bool, default=False)

    def on_init(self):
        if self.session is None:
            self.session = str(uuid.uuid4())
        if self.logger is None:
            self.configure_logger()
        self.build_despatch_table()

    def build_despatch_table(self):
        self.logger.debug("Building Broadworks despatch table")
        despatch_table = {}
        for module in (broadworks_ocip.responses, broadworks_ocip.requests):
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
        self.despatch_table = despatch_table
        self.logger.debug("Built Broadworks despatch table")

    def configure_logger(self):
        logger = logging.getLogger("broadworks_api")
        logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(FORMATTER)
        logger.addHandler(console_handler)
        self.logger = logger

    def decode_xml(self, xml):
        root = etree.fromstring(xml)
        if root.tag != "{C}BroadsoftDocument":
            raise ValueError
        self.logger.debug("Decoding BroadsoftDocument")
        for element in root:
            if element.tag == "command":
                command = element.get("{http://www.w3.org/2001/XMLSchema-instance}type")
                self.logger.debug(f"Decoding command {command}")
                cls = self.despatch_table[command]
                result = cls._build_from_etree(element)
                return result


# end
