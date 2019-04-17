#!/usr/bin/env python
#
# A derivitive port of:
# https://github.com/oriansj/stage0/blob/master/vm_minimal.c
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

from sys import stderr
from string import hexdigits

from pythoncompat import print_func
from constants import EXIT_SUCCESS, EXIT_FAILURE
from knightdecode import \
    MEM, HALTED, \
    create_vm, grow_memory, \
    read_and_eval, read_and_eval16, read_and_eval32, read_and_eval64

def load_program(vm, romfilename):
    # binary mode because we don't want python's opinion of encoding, newlines
    f = open(romfilename, 'rb')
    f.seek(0,2) # seek to end so we can find filesize
    filesize = f.tell()
    f.seek(0)
    # this is intended to operate at the start of memory before allocation
    assert len(vm[MEM])==0
    vm[MEM].fromfile(f, filesize)
    f.close()

def load_hex_program(vm, hexromfilename):
    f = open(hexromfilename)
    first_nyble = True
    accumulator = 0
    # this is intended to operate at the start of memory before allocation
    assert len(vm[MEM])==0
    while True: # until break
        # this is character based I/O, on newer pythons the text encoding
        # could be something other than ASCII, UTF8, and that's fine
        character = f.read(1)
        if character=='':
            break
        elif character in hexdigits:
            accumulator += int(character, 16)
            if first_nyble:
                accumulator = accumulator << 4
                first_nyble = False
            else:
                first_nyble = True
                vm[MEM].append(accumulator)
                accumulator = 0
        # else: pass # ignore everything that's not a hexdigit
    f.close()

def execute_vm(vm):
    register_size_bits = vm[REG].itemsize*8
    read_and_eval_table = {
        16: read_and_eval16,
        32: read_and_eval32,
        64: read_and_eval64,
        }
    read_and_eval_register_size_specific = read_and_eval_table.get(
        register_size_bits, read_and_eval)
    while not vm[HALTED]:
        vm = read_and_eval_register_size_specific(vm)

def do_minimal_vm(romfile, romhex=False, memory_size=1<<21):
    vm = create_vm(size=0, registersize=32)
    if romhex:
        load_hex_program(vm, romfile)
    else:
        load_program(vm, romfile)
    grow_memory(vm, memory_size)
    execute_vm(vm)

def main(args):
    if len(args)<2:
        print_func("Usage: %s $FileName" % args[0], file=stderr)
        print_func("Where $FileName is the name of the paper tape of the"
                   "program being run", file=stderr)
        exit(EXIT_FAILURE)
    else: # len(args)>=2
        filename = args[1]

        if len(args)==2:
            do_minimal_vm(filename)
        else:
            assert len(args)>2
            romhex = args[2]=="--rom-hex" # check for rom-hex flag, set romhex
            do_minimal_vm(filename, romhex=romhex)
        exit(EXIT_SUCCESS)

if __name__ == "__main__":
    from sys import argv
    main(argv)
