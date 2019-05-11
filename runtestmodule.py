#!/usr/bin/env python3
#
# Copyright (C) 2019 Mark Jenkins <mark@markjenkins.ca>
# This file is part of knightpies
#
# knightpies is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# knightpies is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with knightpies.  If not, see <http://www.gnu.org/licenses/>.

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
