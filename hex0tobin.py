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

from string import hexdigits
import re

from pythoncompat import write_byte, open_ascii, COMPAT_FALSE, COMPAT_TRUE

def hex_and_whitespace_from_hex0(hex0fd):
    line = hex0fd.readline()
    while len(line)>0:
        # regular expression means # or ; , [0] gets us whatever comes before
        precomment = re.split('#|;', line)[0]
        if len(precomment)>0: # there might be no text prior to # or ;
            yield precomment
        line = hex0fd.readline()

def int_bytes_from_hex0_whitespace_iter(f):
    first_nyble = True
    accumulator = 0
    while True: # until break
        try:
            line = next(f)
        except StopIteration:
            return # break would have same effect
        for character in line:
            if character in hexdigits:
                accumulator += int(character, 16)
                if first_nyble:
                    accumulator = accumulator << 4
                    first_nyble = False
                else:
                    first_nyble = True
                    yield accumulator
                    accumulator = 0
            # else: pass # ignore everything that's not a hexdigit

def int_bytes_from_hex0_fd(input_file_fd):
    for output_byte in int_bytes_from_hex0_whitespace_iter(
            hex_and_whitespace_from_hex0(input_file_fd) ):
        yield output_byte

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
