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

from sys import stderr, exit
from string import hexdigits

from pythoncompat import print_func, COMPAT_FALSE, COMPAT_TRUE
from constants import REG, TOP_OF_PROG_MEM, EXIT_SUCCESS, EXIT_FAILURE
from knightdecode import \
    MEM, HALTED, \
    create_vm, grow_memory, \
    get_read_and_eval_for_register_size

from hex0tobin import int_bytes_from_hex0_fd

def set_top_of_prog_mem(vm, topm):
    return vm[0:TOP_OF_PROG_MEM] + (topm,) + vm[TOP_OF_PROG_MEM+1:]

def load_program(vm, romfilename, top_of_program_mem=0):
    # binary mode because we don't want python's opinion of encoding, newlines
    f = open(romfilename, 'rb')
    f.seek(0,2) # seek to end so we can find filesize
    filesize = f.tell()
    f.seek(0)
    # this is intended to operate at the start of memory before allocation
    assert len(vm[MEM])==0
    vm[MEM].fromfile(f, filesize)
    f.close()
    assert top_of_program_mem <= filesize
    # technically this if/else isn't needed, top_of_program_mem=0 is default
    # anyway from create_vm, but we do this for clarity
    if top_of_program_mem==0:
        return vm
    else:
        return set_top_of_prog_mem(vm, top_of_program_mem)


def load_hex_program(vm, hexromfilename):
    # this is intended to operate at the start of memory before allocation
    assert len(vm[MEM])==0
    f = open(hexromfilename)
    for input_byte in int_bytes_from_hex0_fd(f):
        vm[MEM].append(input_byte)
    f.close()


def execute_vm(vm, optimize=COMPAT_TRUE, halt_print=COMPAT_TRUE):
    if optimize:
        read_and_eval_register_size_specific = \
            get_read_and_eval_for_register_size(vm[REG].itemsize)
    else:
        read_and_eval_register_size_specific = \
            get_read_and_eval_for_register_size(0)
    while not vm[HALTED]:
        vm = read_and_eval_register_size_specific(
            vm, halt_print=halt_print)

def do_minimal_vm(romfile, romhex=COMPAT_FALSE, memory_size=1<<21):
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
