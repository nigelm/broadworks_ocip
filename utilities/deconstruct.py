#!/usr/bin/env python
import argparse

from lxml import etree


def deconstruct(elem, prefix=""):
    print(f"{prefix}tag = {elem.tag}")
    for name, value in sorted(elem.items()):
        print(f"{prefix}  attr: {name} = {value}")
    for name, value in elem.nsmap.items():
        print(f"{prefix}  nsmap: {name} = {value}")
    print(f"{prefix}  content: {elem.text}")
    prefix += ">>"
    for child in elem:
        deconstruct(child, prefix=prefix)


def main():
    parser = argparse.ArgumentParser(description="Rip a document apart")
    parser.add_argument(
        "file", type=str,
    )
    args = parser.parse_args()
    fp = open(args.file, "rb")
    tree = etree.parse(fp)
    print(f"header = {tree.docinfo.xml_version}")
    print(f"header = {tree.docinfo.doctype}")
    print(f"header = {tree.docinfo.public_id}")
    print(f"header = {tree.docinfo.system_url}")
    root = tree.getroot()
    deconstruct(root)


if __name__ == "__main__":
    main()
