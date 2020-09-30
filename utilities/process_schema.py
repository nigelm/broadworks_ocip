#!/usr/bin/env python
import argparse
import os
import pickle
import re
import sys
from collections import Counter
from datetime import datetime

import xmlschema
from toposort import toposort_flatten


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def process_element_type(element, params, phash, prefix):
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
        elif phash["is_array"]:
            thistype = "list"
    params.append(f"type={thistype}")
    phash["type"] = thistype


def process_class_elements(file, xsd_component, prefix=""):
    element_hash = {}
    for elem in xsd_component.content_type.iter_elements():
        name = camel_to_snake(elem.name)
        params = []
        is_required = True if elem.min_occurs > 0 else False
        if elem.min_occurs == 0 and elem.max_occurs is None:
            is_array = True
        else:
            is_array = False
        phash = {
            "name": name,
            "xmlname": elem.name,
            "is_required": is_required,
            "is_array": is_array,
            "is_table": False,
            "unknown": False,
        }
        process_element_type(elem, params, phash, prefix)
        params.append(f"required={is_required}")
        phash["params"] = params
        element_hash[name] = phash
    #
    # output the list of elements used for input and output
    file.write("    _ELEMENTS = (\n")
    for item in element_hash.values():
        comment = "  # unknown" if item["unknown"] else ""
        file.write(
            f'        E("{item["name"]}", "{item["xmlname"]}", {item["type"]}, '
            f'{item["is_complex"]}, {item["is_required"]}, {item["is_array"]}, '
            f'{item["is_table"]}, ),{comment}\n',
        )
    file.write("    )\n")
    for item in element_hash.values():
        params = item["params"]
        param_str = ", ".join(params) + ", "
        # build the comment up with name/types etc
        comment_bits = [f"{item['type']}:"]
        if item["is_required"]:
            comment_bits.append("*Required*")
        else:
            comment_bits.append("*Optional*")
        comment_bits.append(item["xmlname"])
        if item["is_array"]:
            comment_bits.append(" *Array*")
        if item["is_table"]:
            comment_bits.append(" *Tabular*")
        comment_length = 0
        file.write("    #:")
        for comment_bit in comment_bits:
            if comment_length > 0 and comment_length + len(comment_bit) > 80:
                file.write("\n    #:")
                comment_length = 0
            file.write(" " + comment_bit)
            comment_length += len(comment_bit)
        file.write("\n")
        file.write(f"    {item['name']} = Field({param_str})\n")


def process_documentation(file, xsd_component):
    anno = xsd_component.annotation
    lines = []
    if anno:
        for doc in anno.documentation:
            for line in doc.text.splitlines():
                line = line.replace("\t", "    ")
                line = line.strip()
                line = re.sub(
                    r"\b([A-Z][A-Za-z0-9]*(?:Request|Response)(?:\d+(?:(?:mp|sp|V)\d+)?)?)\b",
                    r"``\1()``",
                    line,
                )
                line = re.sub(r"^Replaced [Bb]y:", r"Replaced By", line)
                while len(line) > 90:
                    pos = line.rfind(" ", 35, 82)
                    if pos < 0:
                        pos = line.find(" ", 30)
                    if pos > 0:
                        lines.append(line[:pos].strip())
                        line = line[pos + 1 :].strip()
                    else:
                        break
                lines.append(line)
        # strip leading and trailing blank lines
        while len(lines) > 0 and len(lines[0]) == 0:
            del lines[0]
        while len(lines) > 0 and len(lines[-1]) == 0:
            del lines[-1]
        if len(lines) > 0:
            # output the documentation bits
            file.write('    """\n')
            for line in lines:
                line = line.rstrip()  # trailing spaces gives check errors
                if len(line) > 0:
                    file.write(f"    {line}\n")
                else:
                    file.write("\n")
            file.write('    """\n\n')


def process_request(file, xsd_component):
    file.write(f"class {xsd_component.name}(OCIRequest):\n")
    process_documentation(file, xsd_component)
    process_class_elements(file, xsd_component, "OCI.")
    file.write("\n\n")


def process_response(file, xsd_component):
    file.write(f"class {xsd_component.name}(OCIResponse):\n")
    process_documentation(file, xsd_component)
    process_class_elements(file, xsd_component, "OCI.")
    file.write("\n\n")


def process_type(file, xsd_component):
    file.write(f"class {xsd_component.name}(OCIType):\n")
    process_documentation(file, xsd_component)
    process_class_elements(file, xsd_component)
    file.write("\n\n")


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
            for elem in xsd_component.content_type.iter_elements():
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
        out.write("from classforge import Field\n\n")
        if thing in ("request", "response"):
            out.write("import broadworks_ocip.types as OCI\n")
        out.write("from .base import ElementInfo as E\n")
        out.write(f"from .base import OCI{thing.title()}\n")
        out.write("\n\n")
        results.append(out)
    return results[0], results[1], results[2]


def close_output_files(types_file, requests_file, responses_file):
    for out in (types_file, requests_file, responses_file):
        out.write("\n# end\n\n")


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
