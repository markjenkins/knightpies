#!/usr/bin/env python
#
# Copyright (C) 2020 Mark Jenkins <mark@markjenkins.ca>
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

from pythoncompat import COMPAT_TRUE, open_ascii
from M1 import M1_file_objs_to_hex2_file
from hex2tobin import write_binary_filefd_from_hex2_filefd

# TODO, look into python version compatibility
from StringIO import StringIO

def M1_files_objs_to_bin(input_file_objs, output_file_obj):
    hex2_file_obj = StringIO()
    M1_file_objs_to_hex2_file(input_file_objs, hex2_file_obj)
    hex2_file_obj.seek(0) # rewind after above finishes reading
    write_binary_filefd_from_hex2_filefd(hex2_file_obj, output_file_obj)

def M1_files_to_bin(input_filenames, output_filename, close_after=COMPAT_TRUE):
    input_file_objs = [ open_ascii(filename) for filename in input_filenames ]
    output_file_obj = open(output_filename, 'wb')
    M1_files_objs_to_bin(input_file_objs, output_file_obj)
    if close_after:
        output_file_obj.close()
        for f in input_file_objs:
            f.close()

def main():
    from sys import argv
    arguments = argv[1:]
    if len(arguments) == 2:
        input_filenames = [arguments[0]]
        output_filename = arguments[1]
    elif len(arguments) > 2:
        input_filenames = []
        output_filename = None
        args_iter = iter(arguments)
        while COMPAT_TRUE:
            try:
                arg = next(args_iter)
            except StopIteration:
                break
            if arg == '-o' or arg == '--output':
                output_filename = next(args_iter)
            else:
                input_filenames.append(arg)
        if output_filename == None:
            raise Exception("You must use -o or --output when there is more "
                            "than 1 input file")


    M1_files_to_bin(input_filenames, output_filename, close_after=COMPAT_TRUE)

if __name__ == "__main__":
    main()
