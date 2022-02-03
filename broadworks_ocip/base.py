"""
Broadworks OCI-P Interface Base Classes

Base classes used by the types, requests and responses as well as
other components like ElementInfo that are used by those.
"""
import re
from collections import namedtuple
from typing import Any
from typing import Dict
from typing import Tuple

import attr
from lxml import etree

from broadworks_ocip.exceptions import OCIErrorAPISetup
from broadworks_ocip.exceptions import OCIErrorAttributeMissing
from broadworks_ocip.exceptions import OCIErrorResponse
from broadworks_ocip.exceptions import OCIErrorUnexpectedAttribute


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


class OCIType:
    """
    OCIType - Base type for all the OCI-P component classes
    """

    __slots__ = ["_frozen"]

    def __init__(self, **kwargs):
        for elem in self._elements():
            if elem.name in kwargs:
                setattr(self, elem.name, kwargs[elem.name])
                if elem.is_required and kwargs[elem.name] is None:
                    raise OCIErrorAttributeMissing(
                        message=f"Required attribute {elem.name} is missing",
                    )
                del kwargs[elem.name]
            elif elem.is_required:
                raise OCIErrorAttributeMissing(
                    message=f"Required attribute {elem.name} is missing",
                )
            else:
                setattr(self, elem.name, None)
        if kwargs:
            raise OCIErrorUnexpectedAttribute(
                message=f"Unexpected attribute(s) {kwargs.keys()}",
            )
        self._frozen = True

    def __delattr__(self, *args, **kwargs):
        if hasattr(self, "_frozen"):
            raise AttributeError("This object is frozen!")
        object.__delattr__(self, *args, **kwargs)

    def __setattr__(self, *args, **kwargs):
        if hasattr(self, "_frozen"):
            raise AttributeError("This object is frozen!")
        object.__setattr__(self, *args, **kwargs)

    # Namespace maps used for various XML build tasks
    @classmethod
    def _default_nsmap(cls):
        return {None: "", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

    @classmethod
    def _document_nsmap(cls):
        return {None: "C", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

    @classmethod
    def _error_nsmap(cls):
        return {
            "c": "C",
            None: "",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }

    @classmethod
    def _elements(cls) -> Tuple[ElementInfo, ...]:
        raise OCIErrorAPISetup(message="_elements should be defined in the subclass.")

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
        element = etree.Element(name, nsmap=self._default_nsmap())
        return self.etree_sub_components_(element)

    def etree_sub_components_(self, element: "etree._Element"):
        """
        Build XML etree subelements for the components within this OCIType

        Arguments:
            element: The parent element that the components are to be attached to

        Returns:
            etree: etree.Element() for this class
        """
        for sub_element in self._elements():
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
                    nsmap=self._default_nsmap(),
                )
        elif sub_element.is_table:
            # any table should be a list of namedtuple elements
            if type(value) is list and len(value) > 0:
                elem = etree.SubElement(
                    element,
                    sub_element.xmlname,
                    nsmap=self._default_nsmap(),
                )
                first = value[0]
                for col in first._fields:
                    col_heading = etree.SubElement(elem, "colHeading")
                    col_heading.text = self.snake_case_to_column_header(col)
                for row in value:
                    row_item = etree.SubElement(elem, "row")
                    for col in row:
                        col_item = etree.SubElement(row_item, "col")
                        col_item.text = col
        elif sub_element.is_complex:
            elem = etree.SubElement(
                element,
                sub_element.xmlname,
                nsmap=self._default_nsmap(),
            )
            value.etree_sub_components_(elem)
        else:
            elem = etree.SubElement(
                element,
                sub_element.xmlname,
                nsmap=self._default_nsmap(),
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

    def snake_case_to_column_header(self, snake_str):
        """
        Converts a pythonic snake case name into a column header name

        Arguments:
            header: The header name in snake lower case

        Returns:
            snake: initial capital and space separated result name
        """
        components = snake_str.split("_")
        # We capitalize the first letter of each component except the first one
        # with the 'title' method and join them together.
        return " ".join(x.title() for x in components)

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
    def build_from_node_(cls, elem: ElementInfo, node: "etree._Element"):
        """
        Creates an OCI subelement from a single  XML etree node

        Arguments:
            elem: The subelement descriptor
            node: The OCITable XML element node

        Returns:
            results: Object instance for this class
        """
        if node is not None:
            if elem.is_table:
                return cls.decode_table_(node)
            elif elem.is_complex:
                return elem.type.build_from_etree_(node)
            elif elem.type == bool:
                return elem.type(
                    True if node.text == "true" else False,
                )
            else:
                return elem.type(node.text)
        else:
            return None

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
        for elem in cls._elements():
            if elem.is_array:
                result = []
                nodes = element.findall(elem.xmlname)
                for node in nodes:
                    result.append(cls.build_from_node_(elem=elem, node=node))
                initialiser[elem.name] = result
            else:
                node = element.find(elem.xmlname)
                if node is not None:
                    initialiser[elem.name] = cls.build_from_node_(elem=elem, node=node)
                # else...
                # I am inclined to thow an error here - at least after checking if
                # the thing is require, but the class builder should do that so lets
                # let it do its thing
        # now have a dict with all the bits in it.
        # use that to build a new object
        return cls(**initialiser)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert object to dict representation of itself

        This was provided as part of the Classforge system, which we have moved away
        from, so this is a local re-implementation.  This is only used within the test
        suite at present.
        """
        elements = {}
        for elem in self._elements():
            value = getattr(self, elem.name)
            if elem.is_table:
                pass
            elif elem.is_complex:
                if elem.is_array:
                    value = [x.to_dict() for x in value]
                else:
                    value = value.to_dict()
            elif elem.is_array:
                value = [x for x in value]
            elements[elem.name] = value
        return elements


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

    __slots__ = ["_frozen", "session_id"]

    def __init__(
        self,
        session_id: str = "00000000-1111-2222-3333-444444444444",
        **kwargs,
    ):
        self.session_id = session_id
        super().__init__(**kwargs)

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
            nsmap=self._document_nsmap(),
        )
        #
        # add the session
        session = etree.SubElement(root, "sessionId", nsmap=self._default_nsmap())
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
            nsmap=self._default_nsmap(),
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

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert object to dict representation of itself

        This was provided as part of the Classforge system, which we have moved away
        from, so this is a local re-implementation.  This is only used within the test
        suite at present.
        """
        elements = super().to_dict()  # pick up the base object data
        elements["session_id"] = self.session_id
        return elements


class OCIRequest(OCICommand):
    """
    OCIRequest - base class for all OCI Command Request types
    """

    pass


class OCIResponse(OCICommand):
    """
    OCIResponse - base class for all OCI Command Response types
    """

    def build_xml_command_element_(self, root: "etree._Element"):
        """
        Build the XML etree of the main command element of the current Command
        Responses have an echo attribute in the element.

        :rtype: etree.Element()
        """
        return etree.SubElement(
            root,
            "command",
            {"echo": "", "{http://www.w3.org/2001/XMLSchema-instance}type": self.type_},
            nsmap=self._default_nsmap(),
        )


class SuccessResponse(OCIResponse):
    """
    The SuccessResponse is concrete response sent whenever a transaction is successful
    and does not return any data.
    """

    __slots__ = ["_frozen", "session_id"]

    @classmethod
    def _elements(cls) -> Tuple[ElementInfo, ...]:
        return ()


class ErrorResponse(OCIResponse):
    """
    The ErrorResponse is concrete response sent whenever a transaction fails
    and does not return any data.

    As this an error, when it is created from an incoming command response, a
    `OCIErrorResponse` exception is raised in `post_xml_decode_`.
    """

    __slots__ = [
        "error_code",
        "summary",
        "summary_english",
        "detail",
        "type",
        "_frozen",
        "session_id",
    ]

    @classmethod
    def _elements(cls) -> Tuple[ElementInfo, ...]:
        return (
            ElementInfo("error_code", "errorCode", int),
            ElementInfo("summary", "summary", str, is_required=True),
            ElementInfo("summary_english", "summaryEnglish", str, is_required=True),
            ElementInfo("detail", "detail", str),
            ElementInfo("type", "type", str),
        )

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
            nsmap=self._error_nsmap(),
        )


# end
