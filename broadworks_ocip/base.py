from collections import namedtuple

from classforge import Class
from classforge import Field
from lxml import etree


class ElementInfo(
    namedtuple(
        "ElementInfo", ["name", "xmlname", "is_complex", "is_required", "is_table"],
    ),
):
    pass


class OCISession:
    __instance = None

    def __init__(self, session=None):
        """ Virtually private constructor. """
        if OCISession.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            OCISession.__instance = self
        self.session = session


class OCIType(Class):
    def _xml_sub_components(self, element):
        for sub_element in self.ELEMENTS:
            value = getattr(self, sub_element.name)
            if value is None:
                if sub_element.is_required:
                    etree.SubElement(
                        element,
                        sub_element.xmlname,
                        {"{http://www.w3.org/2001/XMLSchema-instance}nil": "true"},
                    )
            elif sub_element.is_complex:
                sub_element.append(value._xml_components(sub_element.xmlname))
            else:
                elem = etree.SubElement(element, sub_element.xmlname)
                elem.text = value
        return element

    def _xml_components(self, name=None):
        if name is None:
            name = self.__class__.__name__
        element = etree.Element(name)
        return self._xml_sub_components(element)


class OCIRequest(OCIType):
    def get_xml(self):
        # document root element
        root = etree.Element(
            "BroadsoftDocument",
            {
                "protocol": "OCI",
                "xmlns": "C",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            },
        )
        #
        # add the session
        sess = etree.SubElement(root, "sessionId", {"xmlns": ""})
        sess.text = OCISession.session
        #
        # and the command
        element = etree.SubElement(
            root, "command", {"xmlns": "", "xsi:type": self.__class__.__name__},
        )
        self._xml_sub_components(element)  # attach parameters etc
        #
        # wrap a tree around it
        tree = etree.ElementTree(root)
        return tree.tostring(pretty_print=True)


class OCIResponse(OCIType):
    pass


# end
