#!/usr/bin/env python3

from sys import argv
from os.path import split as path_split, join as path_join, splitext, exists
from unittest import main
from itertools import chain

def recursively_get_package_components(path):
    if exists(path_join(path, "__init__.py")):
        parent, child = path_split(path)
        yield from recursively_get_package_components(parent)
        yield child

def get_module_for_file(filepath):
    path_to, filename = path_split(filepath)
    modulename, ext = splitext(filename)
    return '.'.join(
        chain(recursively_get_package_components(path_to),
              (modulename,)
        ) # chain
    ) # join

if __name__ == "__main__":
    if len(argv)>1:
        main( module=get_module_for_file(argv[1]), argv=(argv[0],) )
