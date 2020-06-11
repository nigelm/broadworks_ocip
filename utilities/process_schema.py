#!/usr/bin/env python
import argparse
import os
import pickle
import re
import sys
from collections import Counter

import xmlschema
from toposort import toposort_flatten


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def process_element_type(element, params, phash):
    type = element.type
    is_complex = type.is_complex()
    phash["is_complex"] = is_complex
    if is_complex:
        if type.name is not None:
            if element.type.name == "{C}OCITable":
                params.append("type=list")
                phash["is_table"] = True
            elif element.type.name.startswith("{"):
                params.append("type=str")
                phash["unknown"] = True  # TODO more complex type handling
            else:
                params.append(f"type={element.type.name}")
        else:
            params.append("type=str")
            phash["unknown"] = True  # TODO more complex type handling
    else:
        if type.primitive_type.id == "boolean":
            params.append("type=bool")
        elif type.primitive_type.id == "decimal":
            params.append("type=int")
        else:
            params.append("type=str")


def process_class_elements(file, xsd_component):
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
        process_element_type(elem, params, phash)
        params.append(f"required={is_required}")
        phash["params"] = params
        element_hash[name] = phash
    #
    # output the list of elements used for input and output
    file.write("    ELEMENTS = (\n")
    for item in element_hash.values():
        comment = "  # unknown" if item["unknown"] else ""
        file.write(
            f'        ElementInfo("{item["name"]}", "{item["xmlname"]}", '
            f'{item["is_complex"]}, {item["is_required"]}, {item["is_table"]}),'
            f"{comment}\n",
        )
    file.write("    )\n")
    for item in element_hash.values():
        params = item["params"]
        param_str = ", ".join(params)
        file.write(f"    {item['name']} = Field({param_str})\n")


def process_request(file, xsd_component):
    file.write(f"class {xsd_component.name}(OCIRequest):\n")
    process_class_elements(file, xsd_component)
    file.write("\n\n")


def process_response(file, xsd_component):
    file.write(f"class {xsd_component.name}(OCIResponse):\n")
    process_class_elements(file, xsd_component)
    file.write("\n\n")


def process_type(file, xsd_component):
    file.write(f"class {xsd_component.name}(OCIType):\n")
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
    for thing in ("types", "requests", "responses"):
        filename = os.path.join("broadworks_ocip", thing + ".py")
        out = open(filename, "w")
        out.write("from broadworks_ocip.base import *\n")
        if thing in ("requests", "responses"):
            out.write("from broadworks_ocip.types import *\n")
        if thing == "requests":
            out.write("from broadworks_ocip.responses import *\n")
        out.write("from classforge import Field\n\n\n")
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
