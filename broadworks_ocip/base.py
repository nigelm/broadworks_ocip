"""
Broadworks OCI-P Interface Base Classes

Base classes used by the types, requests and responses as well as
other components like ElementInfo that are used by those.
"""
import re
from collections import namedtuple

from classforge import Class
from classforge import Field
from lxml import etree

from broadworks_ocip.exceptions import OCIErrorResponse


class ElementInfo(
    namedtuple(
        "ElementInfo",
        [
            "name",
            "xmlname",
            "type",
            "is_complex",
            "is_required",
            "is_array",
            "is_table",
        ],
    ),
):
    """
    ElementInfo - information on each element of a Broadsoft OCIType

    Used to describe the element when serialising to/from XML
    """

    pass


class OCIType(Class):
    """
    OCIType - Base type for all the OCI-P component classes
    """

    _DEFAULT_NSMAP = {None: "", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    _DOCUMENT_NSMAP = {None: "C", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    _ERROR_NSMAP = {
        "c": "C",
        None: "",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    @property
    def _type(self):
        return self.__class__.__name__

    def _post_xml_decode(self):
        """
        Carry out any operations after the XML decode

        Intended for use by subclasses where they need to take actions immediately
        after they are created from an incoming XML document.
        """
        pass

    def _etree_components(self, name=None):
        """
        Build XML etree element tree for this OCIType

        :param name: The name or tag of the element - defaults to the ``_type``
        :type name: string
        :rtype: etree.Element()

        """
        if name is None:
            name = self._type
        element = etree.Element(name, nsmap=self._DEFAULT_NSMAP)
        return self._etree_sub_components(element)

    def _etree_sub_components(self, element):
        """
        Build XML etree subelements for the components within this OCIType

        :param element: The element that is the parent of the subelements
        :type element: etree.Element()
        :rtype: etree.Element()

        """
        for sub_element in self._ELEMENTS:
            value = getattr(self, sub_element.name)
            if sub_element.is_array:
                if value is not None:
                    for subvalue in value:
                        self._etree_sub_element(element, sub_element, subvalue)
            else:
                self._etree_sub_element(element, sub_element, value)
        return element

    def _etree_sub_element(self, element, sub_element, value):
        """
        Build XML etree subelement for one elemnt within this OCIType

        :param element: The element that is the parent of the subelements
        :type element: etree.Element()
        :rtype: etree.Element()

        """
        if value is None:
            if sub_element.is_required:
                etree.SubElement(
                    element,
                    sub_element.xmlname,
                    {"{http://www.w3.org/2001/XMLSchema-instance}nil": "true"},
                    nsmap=self._DEFAULT_NSMAP,
                )
        elif sub_element.is_complex:
            elem = etree.SubElement(
                element,
                sub_element.xmlname,
                nsmap=self._DEFAULT_NSMAP,
            )
            value._etree_sub_components(elem)
        else:
            elem = etree.SubElement(
                element,
                sub_element.xmlname,
                nsmap=self._DEFAULT_NSMAP,
            )
            if sub_element.type == bool:
                elem.text = "true" if value else "false"
            elif sub_element.type == int:
                elem.text = str(value)
            else:
                elem.text = value

    @classmethod
    def _column_header_snake_case(cls, header):
        """
        Converts an XML name into a pythonic snake case name

        :param header: The name to convert
        :type header: string
        :rtype: string

        """
        return re.sub("[ _]+", r"_", header).lower()

    @classmethod
    def _decode_table(cls, element):
        """
        Decode a table (used in a OCIResponse) into a list of named tuples

        :param element:
        :rtype: list of named tuples

        """
        typename = element.tag
        results = []
        columns = [
            cls._column_header_snake_case(b.text)
            for b in element.iterfind("colHeading")
        ]
        type = namedtuple(typename, columns)
        for row in element.iterfind("row"):
            rowdata = [b.text for b in row.iterfind("col")]
            rowobj = type(*rowdata)
            results.append(rowobj)
        return results

    @classmethod
    def _build_from_etree(cls, element):
        """
        Create an OciType based instance from an XML etree element

        :param element: XML etree element
        :type element: etree.Element()
        :rtype: cls instance

        """
        initialiser = {}
        for elem in cls._ELEMENTS:
            if elem.is_array:
                result = []
                nodes = element.findall(elem.xmlname)
                for node in nodes:
                    result.append(node.text)
                initialiser[elem.name] = result
            else:
                node = element.find(elem.xmlname)
                if node is not None:
                    if elem.is_table:
                        initialiser[elem.name] = cls._decode_table(node)
                    elif elem.is_complex:
                        initialiser[elem.name] = elem.type._build_from_etree(node)
                    else:
                        initialiser[elem.name] = elem.type(node.text)
                # else...
                # I am inclined to thow an error here - at least after checking if
                # the thing is require, but the class builder should do that so lets
                # let it do its thing
        # now have a dict with all the bits in it.
        # use that to build a new object
        return cls(**initialiser)


class OCICommand(OCIType):
    """
    OCICommand - base class for all OCI Command (Request/Response) types
    """

    _session = Field(type=str, default="00000000-1111-2222-3333-444444444444")

    def _build_xml(self):
        """
        Build an XML document of the current Command (Request/Response)

        :rtype: string containing XML document
        """
        # document root element
        root = etree.Element(
            "{C}BroadsoftDocument",
            {"protocol": "OCI"},
            nsmap=self._DOCUMENT_NSMAP,
        )
        #
        # add the session
        sess = etree.SubElement(root, "sessionId", nsmap=self._DEFAULT_NSMAP)
        sess.text = self._session
        #
        # and the command
        element = self._build_xml_command_element(root)
        self._etree_sub_components(element)  # attach parameters etc
        #
        # wrap a tree around it
        tree = etree.ElementTree(root)
        return etree.tostring(
            tree,
            xml_declaration=True,
            encoding="ISO-8859-1",
            # standalone=False,
            # pretty_print=True,
        )

    def _build_xml_command_element(self, root):
        """
        Build the XML etree of the main command element of the current Command
        Intended to be overridden in a subclass for the few elements that do things
        a little differently (for example errors).

        :rtype: etree.Element()
        """
        return etree.SubElement(
            root,
            "command",
            {"{http://www.w3.org/2001/XMLSchema-instance}type": self._type},
            nsmap=self._DEFAULT_NSMAP,
        )


class OCIRequest(OCICommand):
    """
    OCIRequest - base class for all OCI Command Request types
    """

    pass


class OCIResponse(OCICommand):
    """
    OCIResponse - base class for all OCI Command Response types
    """

    pass


class SuccessResponse(OCIResponse):
    """
    The SuccessResponse is concrete response sent whenever a transaction is successful
    and does not return any data.
    """

    _ELEMENTS = ()  # type: ignore # type: Tuple[Tuple]


class ErrorResponse(OCIResponse):
    """
    The ErrorResponse is concrete response sent whenever a transaction fails and does not return any data.
    """

    _ELEMENTS = (
        ElementInfo("error_code", "errorCode", int, False, False, False, False),
        ElementInfo("summary", "summary", str, False, True, False, False),
        ElementInfo(
            "summary_english",
            "summaryEnglish",
            str,
            False,
            True,
            False,
            False,
        ),
        ElementInfo("detail", "detail", str, False, False, False, False),
        ElementInfo("type", "type", str, False, False, False, False),
    )
    error_code = Field(type=int, required=False)
    summary = Field(type=str, required=True)
    summary_english = Field(type=str, required=True)
    detail = Field(type=str, required=False)
    type = Field(type=str, required=False)

    def _post_xml_decode(self):
        """Raise an exception as this is an error"""
        raise OCIErrorResponse(
            object=self,
            message=f"{self.error_code}: {self.summary} - {self.detail}",
        )

    def _build_xml_command_element(self, root):
        return etree.SubElement(
            root,
            "command",
            {
                "type": "Error",
                "echo": "",
                "{http://www.w3.org/2001/XMLSchema-instance}type": "c:" + self._type,
            },
            nsmap=self._ERROR_NSMAP,
        )


# end
