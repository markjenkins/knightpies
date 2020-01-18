#!/usr/bin/env python
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

from __future__ import generators # for yield keyword in python 2.2

from string import hexdigits

from pythoncompat import write_byte, open_ascii, COMPAT_FALSE, COMPAT_TRUE

def int_bytes_from_hex0_fd(input_file_fd):
    first_nyble = COMPAT_TRUE
    accumulator = 0
    comment = COMPAT_FALSE
    character = input_file_fd.read(1)
    while len(character)>0:
        if not comment and (character==';' or character=='#'):
            comment = COMPAT_TRUE
        elif comment and (character=='\r' or character=='\n'):
            comment = COMPAT_FALSE
        elif not comment and character in hexdigits:
            accumulator += int(character, 16)
            if first_nyble:
                accumulator = accumulator << 4
                first_nyble = COMPAT_FALSE
            else:
                first_nyble = COMPAT_TRUE
                yield accumulator
                accumulator = 0
        # else: pass # ignore everything that's not a hexdigit
        character = input_file_fd.read(1)

def write_binary_filefd_from_hex0_filefd(input_file_fd, output_file_fd):
    for output_byte in int_bytes_from_hex0_fd(input_file_fd):
        write_byte(output_file_fd, output_byte)

def write_binary_file_from_hex0_file(input_file, output_file):
    # character based file read, but not UTF-8
    input_file_fd = open_ascii(input_file)
    output_file_fd = open(output_file, 'wb') # binary output
    write_binary_filefd_from_hex0_filefd(input_file_fd, output_file_fd)
    output_file_fd.close()
    input_file_fd.close()

if __name__ == "__main__":
    from sys import argv
    write_binary_file_from_hex0_file(*argv[1:2+1])
