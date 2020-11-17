"""
Broadworks OCI-P Interface Base Classes

Base classes used by the types, requests and responses as well as
other components like ElementInfo that are used by those.
"""
import re
from collections import namedtuple

import attr
from classforge import Class
from classforge import Field
from lxml import etree

from broadworks_ocip.exceptions import OCIErrorResponse


@attr.s(slots=True, frozen=True)
class ElementInfo:
    """
    ElementInfo - information on each element of a Broadsoft OCIType

    Used to describe the element when serialising to/from XML

    Attributes:
        name: name of this element (in python snake case)
        xmlname: name of this element (in Java like camel case)
        type: the type of the resulting element
        is_complex: is this a complex element - containing another OCIType derived class
        is_required: Is this required (True) or Optional (False)
        is_array: Is this an array/list of element values
        is_table: Is this a Broadworks table type - only seen in Responses
    """

    name: str = attr.ib()
    xmlname: str = attr.ib()
    type = attr.ib()
    is_complex: bool = attr.ib(default=False)
    is_required: bool = attr.ib(default=False)
    is_array: bool = attr.ib(default=False)
    is_table: bool = attr.ib(default=False)


class OCIType(Class):
    """
    OCIType - Base type for all the OCI-P component classes
    """

    # Namespace maps used for various XML build tasks
    DEFAULT_NSMAP = {None: "", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    DOCUMENT_NSMAP = {None: "C", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    ERROR_NSMAP = {
        "c": "C",
        None: "",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    @property
    def type_(self):
        """Return the typename of the class"""
        return self.__class__.__name__

    def post_xml_decode_(self):
        """
        Carry out any operations after the XML decode

        Intended for use by subclasses where they need to take actions immediately
        after they are created from an incoming XML document.
        """
        pass

    def etree_components_(self, name=None):
        """
        Build XML etree element tree for this OCIType

        Arguments:
            name: The name or tag of the element - defaults to the `type_`

        Returns:
            etree: etree.Element() for this class
        """
        if name is None:
            name = self.type_
        element = etree.Element(name, nsmap=self.DEFAULT_NSMAP)
        return self.etree_sub_components_(element)

    def etree_sub_components_(self, element: "etree._Element"):
        """
        Build XML etree subelements for the components within this OCIType

        Arguments:
            element: The parent element that the components are to be attached to

        Returns:
            etree: etree.Element() for this class
        """
        for sub_element in self._ELEMENTS:
            value = getattr(self, sub_element.name)
            if sub_element.is_array:
                if value is not None:
                    for subvalue in value:
                        self.etree_sub_element_(element, sub_element, subvalue)
            else:
                self.etree_sub_element_(element, sub_element, value)
        return element

    def etree_sub_element_(
        self,
        element: "etree._Element",
        sub_element: "ElementInfo",
        value,
    ):
        """
        Build XML etree subelement for one elemnt within this OCIType

        Arguments:
            element: The parent element that the components are to be attached to
            sub_element: The definition of the sub element to be attached
            value: Value of the sub element - quite possibly None

        Returns:
            etree: etree.Element() for this class
        """
        if value is None:
            if sub_element.is_required:
                etree.SubElement(
                    element,
                    sub_element.xmlname,
                    {"{http://www.w3.org/2001/XMLSchema-instance}nil": "true"},
                    nsmap=self.DEFAULT_NSMAP,
                )
        elif sub_element.is_complex:
            elem = etree.SubElement(
                element,
                sub_element.xmlname,
                nsmap=self.DEFAULT_NSMAP,
            )
            value.etree_sub_components_(elem)
        else:
            elem = etree.SubElement(
                element,
                sub_element.xmlname,
                nsmap=self.DEFAULT_NSMAP,
            )
            if sub_element.type == bool:
                elem.text = "true" if value else "false"
            elif sub_element.type == int:
                elem.text = str(value)
            else:
                elem.text = value

    @classmethod
    def column_header_snake_case_(cls, header):
        """
        Converts an XML name into a pythonic snake case name

        Arguments:
            header: The header name in space separated words

        Returns:
            snake: lower cased and underscore separated result name
        """
        return re.sub("[ _]+", r"_", header).lower()

    @classmethod
    def decode_table_(cls, element: "etree._Element"):
        """
        Decode a table (used in a OCIResponse) into a list of named tuples

        Arguments:
            element: The OCITable XML element

        Returns:
            results: List of namedtuple elements, one for each table row
        """
        typename: str = element.tag
        results = []
        columns = [
            cls.column_header_snake_case_(b.text)
            for b in element.iterfind("colHeading")
        ]
        type = namedtuple(typename, columns)  # type: ignore
        for row in element.iterfind("row"):
            rowdata = [b.text for b in row.iterfind("col")]
            rowobj = type(*rowdata)
            results.append(rowobj)
        return results

    @classmethod
    def build_from_etree_non_parameters_(
        cls,
        element: "etree._Element",
        initialiser: dict,
    ):
        """
        Handle any items outside the parameter set

        Intended for use by subclasses where they need to take actions immediately
        after they are created from an incoming XML document.
        """
        pass

    @classmethod
    def build_from_etree_(cls, element: "etree._Element"):
        """
        Create an OciType based instance from an XML etree element

        Arguments:
            element: The OCITable XML element

        Returns:
            results: Object instance for this class
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
                        initialiser[elem.name] = cls.decode_table_(node)
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

    Attributes:
        session_id: The session ID used for the command exchange.  We use
            UUIDs by default, although this is not required.  The default
            is fixed on here (but normally passed in from the containing
            API object) - do not use the default in production - its simply
            there to give a known value for testing.
    """

    session_id: str = Field(type=str, default="00000000-1111-2222-3333-444444444444")

    def build_xml_(self):
        """
        Build an XML document of the current Command (Request/Response)

        Parameters:

        Returns:
            xml: string containing XML document
        """
        # document root element
        root = etree.Element(
            "{C}BroadsoftDocument",
            {"protocol": "OCI"},
            nsmap=self.DOCUMENT_NSMAP,
        )
        #
        # add the session
        session = etree.SubElement(root, "sessionId", nsmap=self.DEFAULT_NSMAP)
        session.text = self.session_id
        #
        # and the command
        element = self.build_xml_command_element_(root)
        self.etree_sub_components_(element)  # attach parameters etc
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

    def build_xml_command_element_(self, root: "etree._Element"):
        """
        Build the XML etree of the main command element of the current Command
        Intended to be overridden in a subclass for the few elements that do things
        a little differently (for example errors).

        :rtype: etree.Element()
        """
        return etree.SubElement(
            root,
            "command",
            {"{http://www.w3.org/2001/XMLSchema-instance}type": self.type_},
            nsmap=self.DEFAULT_NSMAP,
        )

    @classmethod
    def build_from_etree_non_parameters_(
        cls,
        element: "etree._Element",
        initialiser: dict,
    ):
        """
        Pick up the session id from the command set

        Overrides the class method defined in OCIType.
        """
        node = element.find("sessionId")
        if node is not None:
            initialiser["session_id"] = node.text


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
    The ErrorResponse is concrete response sent whenever a transaction fails
    and does not return any data.

    As this an error, when it is created from an incoming command response, a
    `OCIErrorResponse` exception is raised in `post_xml_decode_`.
    """

    _ELEMENTS = (
        ElementInfo("error_code", "errorCode", int),
        ElementInfo("summary", "summary", str, is_required=True),
        ElementInfo("summary_english", "summaryEnglish", str, is_required=True),
        ElementInfo("detail", "detail", str),
        ElementInfo("type", "type", str),
    )
    error_code = Field(type=int, required=False)
    summary = Field(type=str, required=True)
    summary_english = Field(type=str, required=True)
    detail = Field(type=str, required=False)
    type = Field(type=str, required=False)

    def post_xml_decode_(self):
        """Raise an exception as this is an error"""
        raise OCIErrorResponse(
            object=self,
            message=f"{self.error_code}: {self.summary} - {self.detail}",
        )

    def build_xml_command_element_(self, root):
        return etree.SubElement(
            root,
            "command",
            {
                "type": "Error",
                "echo": "",
                "{http://www.w3.org/2001/XMLSchema-instance}type": "c:" + self.type_,
            },
            nsmap=self.ERROR_NSMAP,
        )


# end
