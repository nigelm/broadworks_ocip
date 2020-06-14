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
    params.append(f"type={thistype}")
    phash["type"] = thistype


def process_class_elements(file, xsd_component, prefix=""):
    element_hash = {}
    for elem in xsd_component.content_type.iter_elements():
        name = camel_to_snake(elem.name)
        params = []
        is_required = True if elem.min_occurs > 0 else False
        phash = {
            "name": name,
            "xmlname": elem.name,
            "is_required": is_required,
            "is_table": False,
            "unknown": False,
        }
        process_element_type(elem, params, phash, prefix)
        params.append(f"required={is_required}")
        phash["params"] = params
        element_hash[name] = phash
    #
    # output the list of elements used for input and output
    file.write("    ELEMENTS = (\n")
    for item in element_hash.values():
        comment = "  # unknown" if item["unknown"] else ""
        file.write(
            f'        ElementInfo("{item["name"]}", "{item["xmlname"]}", {item["type"]}, '
            f'{item["is_complex"]}, {item["is_required"]}, {item["is_table"]}),'
            f"{comment}\n",
        )
    file.write("    )\n")
    for item in element_hash.values():
        params = item["params"]
        param_str = ", ".join(params)
        file.write(f"    {item['name']} = Field({param_str})\n")


def process_documentation(file, xsd_component):
    anno = xsd_component.annotation
    lines = []
    if anno:
        for doc in anno.documentation:
            for line in doc.text.splitlines():
                line = line.replace("\t", "    ")
                if line.isspace():
                    line = ""
                elif line.startswith("        "):
                    line = line[8:]
                while len(line) > 90:
                    pos = line.rfind(" ", 35, 82)
                    if pos < 0:
                        pos = line.find(" ", 30)
                    if pos > 0:
                        lines.append(line[:pos])
                        line = line[pos + 1 :]
                    else:
                        break
                lines.append(line)
        # strip leading and trailing blank lines
        while len(lines) > 0 and len(lines[0]) == 0:
            del lines[0]
        while len(lines) > 0 and len(lines[-1]) == 0:
            del lines[-1]
        # output the documentation bits
        if len(lines) > 0:
            file.write('    """\n')
            for line in lines:
                line = line.rstrip()
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
                r"(Request|Response)(\d+((mp|sp|V)\d+)?)?$", xsd_component.name,
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
        out.write(f"# Broadworks {thing.title()}\n")
        out.write("# Autogenerated from the Broadworks XML Schemas.\n")
        out.write("# Do not edit as changes will be overwritten.\n")
        out.write(f"# Generated on {generation_time.isoformat()}\n")
        out.write("from classforge import Field\n\n")
        if thing in ("request", "response"):
            out.write("import broadworks_ocip.types as OCI\n")
        out.write("from broadworks_ocip.base import ElementInfo\n")
        out.write(f"from broadworks_ocip.base import OCI{thing.title()}\n")
        out.write("\n\n")
        results.append(out)
    return results[0], results[1], results[2]


def main():
    parser = argparse.ArgumentParser(
        description="Parse Broadworks OCI-P schema, build interface code",
    )
    parser.add_argument(
        "--schema", type=str,
    )
    parser.add_argument(
        "--unpickle", action="store_true",
    )
    parser.add_argument(
        "--pickle", action="store_true",
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


if __name__ == "__main__":
    main()
