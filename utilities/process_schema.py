#!/usr/bin/env python
import argparse
import os
import pickle
import re
import sys
from collections import Counter
from datetime import datetime
from textwrap import TextWrapper

import xmlschema
from toposort import toposort_flatten


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def process_element_type(element, phash, prefix):
    type = element.type
    is_complex = type.is_complex()
    phash["is_complex"] = is_complex
    thistype = "str"
    if is_complex:
        if type.name is not None:
            if element.type.name == "{C}OCITable":
                thistype = "list"
                phash["is_table"] = True
            elif element.type.name.startswith("{"):
                phash["unknown"] = True  # TODO more complex type handling
            else:
                thistype = prefix + element.type.name
        else:
            phash["unknown"] = True  # TODO more complex type handling
    else:
        if type.primitive_type.id == "boolean":
            thistype = "bool"
        elif type.primitive_type.id == "decimal":
            thistype = "int"
    phash["type"] = thistype


def build_element_hash(xsd_component, prefix=""):
    element_hash = {}
    for elem in xsd_component.content.iter_elements():
        name = camel_to_snake(elem.name)
        is_required = True if elem.min_occurs > 0 else False
        if is_required and elem.parent.model == "choice":
            is_required = False
        if elem.min_occurs is None:
            if elem.max_occurs is None:
                is_array = False
            elif elem.max_occurs == 1:
                is_array = False
            else:
                is_array = True
        elif elem.min_occurs <= 1 and elem.max_occurs == 1:
            is_array = False
        else:
            is_array = True
        phash = {
            "name": name,
            "xmlname": elem.name,
            "is_required": is_required,
            "is_array": is_array,
            "is_table": False,
            "unknown": False,
        }
        process_element_type(elem, phash, prefix)
        element_hash[name] = phash
    return element_hash


def write_elements(file, elements):
    """Write the _Elements array used for serializing to/from XML"""
    file.write("    @classmethod\n")
    file.write("    def _elements(cls) -> Tuple[E, ...]:\n")
    if len(elements):
        # We have elements - write them out - starting with the header
        file.write("        return (\n")
        for item in elements.values():
            ele = [
                ('"' + item["name"] + '"'),
                ('"' + item["xmlname"] + '"'),
                item["type"],
            ]
            for query in ("is_complex", "is_required", "is_array", "is_table"):
                if item[query]:
                    ele.append(query + "=True")
            comment = "  # unknown" if item["unknown"] else ""
            outstr = " " * 12 + "E(" + ", ".join(ele) + ")," + comment
            if len(outstr) >= 90:
                file.write(" " * 12 + "E(\n")
                for bit in ele:
                    file.write(" " * 16 + bit + ",\n")
                file.write(" " * 12 + ")," + comment + "\n")
            else:
                file.write(outstr + "\n")
        file.write("        )\n")
    else:
        # No elements - we write an empty set out
        file.write("        return ()\n")


def write_attribute_comment(file, element):
    """Write an attribute comment with type and other info for the docs"""
    if element["is_array"]:
        comment_bits = [f"list[{element['type']}]:"]
    else:
        comment_bits = [f"{element['type']}:"]
    if element["is_required"]:
        comment_bits.append("*Required*")
    else:
        comment_bits.append("*Optional*")
    comment_bits.append(element["xmlname"])
    if element["is_array"]:
        comment_bits.append(" *Array*")
    if element["is_table"]:
        comment_bits.append(" *Tabular*")
    wrapper = TextWrapper(
        width=90,
        initial_indent="    #: ",
        subsequent_indent="    #: ",
        break_long_words=False,
    )
    file.write("\n".join(wrapper.wrap(" ".join(comment_bits))) + "\n")


def write_attribute(file, element):
    param_str = "" if element["is_required"] else "default=None"
    if element["is_array"]:
        mytype = f'List[{ element["type"] }]'
    elif element["type"] in ("str", "bool", "int"):
        mytype = element["type"]
    else:
        mytype = '"' + element["type"] + '"'
    outstr = " " * 4 + element["name"] + ": " + mytype + " = attr.ib(" + param_str + ")"
    # if len(outstr) >= 95:
    #    wrapper = TextWrapper(
    #        width=90,
    #        replace_whitespace=False,
    #        initial_indent=" " * 8,
    #        subsequent_indent=" " * 8,
    #        break_long_words=False,
    #    )
    #    file.write(" " * 4 + element["name"] + ": " + mytype + " = attr.ib(\n")
    #    file.write("\n".join(wrapper.wrap(param_str)) + ",\n")
    #    file.write(" " * 4 + ")\n")
    # else:
    #    file.write(outstr + "\n")
    file.write(outstr + "\n")


def process_class_elements(file, elements):
    count = 0
    for element in elements.values():
        # write_attribute_comment(file, element)
        write_attribute(file, element)
        count += 1
    if count > 0:
        file.write("\n")
    write_elements(file, elements)


def process_attribute_documentation(file, elements):
    if len(elements):
        file.write("\n    Attributes:\n")
        wrapper = TextWrapper(
            width=90,
            initial_indent=" " * 8,
            subsequent_indent=" " * 12,
            break_long_words=False,
            drop_whitespace=True,
            fix_sentence_endings=True,
            expand_tabs=False,
        )
        for element in elements.values():
            data = element["name"] + ": " + element["xmlname"]
            file.write("\n".join(wrapper.wrap(data)) + "\n")


def process_documentation(file, xsd_component, elements):
    anno = xsd_component.annotation
    lines = []
    if anno:
        wrapper = TextWrapper(
            width=90,
            initial_indent=" " * 4,
            subsequent_indent=" " * 4,
            break_long_words=False,
            drop_whitespace=True,
            fix_sentence_endings=True,
            expand_tabs=False,
        )
        for doc in anno.documentation:
            # text with leading/trailing spaces stripped
            text = doc.text.strip()
            # text with internal spacing collapsed
            text = re.sub(r"\s+", " ", text)
            # mark up magic method markers
            text = re.sub(
                r"\b([A-Z][A-Za-z0-9]*(?:Request|Response)(?:\d+(?:(?:mp|sp|V)\d+)?)?)\b",
                r"``\1()``",
                text,
            )
            # Fix a standard oddity
            text = re.sub(r"^Replaced [Bb]y:", r"Replaced By", text)
            # break off first sentence
            segments = text.split(".", 1)
            text = segments.pop().lstrip()
            if len(segments) > 0:
                segments[0] += "."  # put the full stop back
            # break off response part if present
            pos = text.find("The response")
            if pos > 0:
                segments.append(text[:pos].rstrip())
                text = text[pos:]
            # break off Replaced By
            pos = text.find("Replaced By")
            if pos > 0:
                segments.append(text[:pos].rstrip())
                segments.append(text[pos:])
            else:
                segments.append(text)
            for mystr in segments:
                if len(lines) > 0:
                    lines.append("")
                lines += wrapper.wrap(mystr)
        if len(lines) > 0:
            # output the documentation bits
            file.write('    """\n' + "\n".join(lines) + "\n")
            process_attribute_documentation(file, elements)
            file.write('    """\n\n')


def process_thing(file, xsd_component, thing, prefix=""):
    file.write("@attr.s(slots=True, frozen=True, kw_only=True)\n")
    file.write(f"class {xsd_component.name}({thing}):\n")
    elements = build_element_hash(xsd_component, prefix)
    process_documentation(file, xsd_component, elements)
    process_class_elements(file, elements)
    file.write("\n\n")


def process_request(file, xsd_component):
    process_thing(file, xsd_component, "OCIRequest", "OCI.")


def process_response(file, xsd_component):
    process_thing(file, xsd_component, "OCIResponse", "OCI.")


def process_type(file, xsd_component):
    process_thing(file, xsd_component, "OCIType", "")


def process_schema(schema, class_list, types_file, requests_file, responses_file):
    for item in class_list:
        xsd_component = schema.types[item]
        if xsd_component.is_complex():
            match = re.search(
                r"(Request|Response)(\d+((mp|sp|V)\d+)?)?$",
                xsd_component.name,
            )
            if match and match.group(1) == "Request":
                process_request(requests_file, xsd_component)
            elif match and match.group(1) == "Response":
                process_response(responses_file, xsd_component)
            else:
                process_type(types_file, xsd_component)


def sort_schema(schema):
    dependancy_map = {}
    for xsd_component in schema.iter_globals():
        if xsd_component.is_complex():
            name = xsd_component.name
            dependancies = Counter()
            for elem in xsd_component.content.iter_elements():
                type = elem.type
                if type.is_complex() and type.name is not None:
                    if re.search(r"^[A-Za-z0-9]+$", type.name):
                        dependancies[type.name] += 1
            dependancy_map[name] = set(dependancies.keys())
    return toposort_flatten(dependancy_map, sort=True)


def open_output_files():
    results = []
    generation_time = datetime.now()
    for thing in ("type", "request", "response"):
        filename = os.path.join("broadworks_ocip", thing + "s.py")
        out = open(filename, "w")
        out.write(f'"""Broadworks OCI-P Interface {thing.title()} Classes"""\n')
        out.write("# Autogenerated from the Broadworks XML Schemas.\n")
        out.write("# Do not edit as changes will be overwritten.\n")
        out.write(f"# Generated on {generation_time.isoformat()}\n")
        out.write("# fmt: off\n")
        out.write("from typing import List\n")
        out.write("from typing import Tuple\n\n")
        out.write("import attr\n\n")
        if thing in ("request", "response"):
            out.write("import broadworks_ocip.types as OCI\n")
        out.write("from .base import ElementInfo as E\n")
        out.write(f"from .base import OCI{thing.title()}\n")
        out.write("\n\n")
        results.append(out)
    return results[0], results[1], results[2]


def close_output_files(types_file, requests_file, responses_file):
    for out in (types_file, requests_file, responses_file):
        out.write("# fmt: on\n")
        out.write("# end\n")


def main():
    parser = argparse.ArgumentParser(
        description="Parse Broadworks OCI-P schema, build interface code",
    )
    parser.add_argument(
        "--schema",
        type=str,
    )
    parser.add_argument(
        "--unpickle",
        action="store_true",
    )
    parser.add_argument(
        "--pickle",
        action="store_true",
    )
    args = parser.parse_args()
    if args.schema:
        schema = xmlschema.XMLSchema(args.schema)
        print("Loaded schema")
        if args.pickle:
            file = open("schema.pkl", "wb")
            pickle.dump(schema, file, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        if args.unpickle:
            file = open("schema.pkl", "rb")
            schema = pickle.load(file)
            print("Unpickled schema")
        else:
            sys.exit("No schema")
    class_list = sort_schema(schema)
    print("Sorted schema")
    types_file, requests_file, responses_file = open_output_files()
    process_schema(schema, class_list, types_file, requests_file, responses_file)
    close_output_files(types_file, requests_file, responses_file)


if __name__ == "__main__":
    main()
