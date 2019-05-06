# A derivitive port of:
# https://github.com/oriansj/stage0/blob/master/vm_instructions.c
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

from __future__ import division # prevent use of "/" in the old way

from knightinstructions import *
from knightinstructions_bit_optimized import make_nbit_optimized_functions

nbit_optimized_dict = make_nbit_optimized_functions(16)

# 1 OP

# We don't need to mess around with sign extension for 16 bit LOADI,
# when copying a signed 16 bit value stored as a 16 bit unsigned into a
# 16 bit unsigned register, we just copy the bits like generic LOADUI does
LOADI = LOADUI

TRUE = nbit_optimized_dict['TRUE_16']


# 3 OP
CMP = nbit_optimized_dict['CMP_16']


# 1 OP immediate
JUMP_P = nbit_optimized_dict['JUMP_P_16']
JUMP_NP = nbit_optimized_dict['JUMP_NP_16']

def CALLI(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    mem_address = register_file[reg0]
    # big endian
    mem[mem_address] = next_ip>>8 # most significant byte
    mem[mem_address+1] = next_ip & 0xFF # least significant byte

    register_file[reg0] += register_file.itemsize # Update our index

    return next_ip + raw_immediate # Update PC
