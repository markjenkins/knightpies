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

nbit_optimized_dict = make_nbit_optimized_functions(64)

# 1 OP
TRUE = nbit_optimized_dict['TRUE_64']

def RET(vm, c):
    mem, register_file, reg0, next_ip_discard = get_args_for_1OP(vm, c)
    reg_size = register_file.itemsize

    # Update our index
    address_of_pc_on_stack = register_file[reg0] - reg_size
    register_file[reg0] = address_of_pc_on_stack

    # Read in the new PC
    # big endian, least significant byte is most significant bits
    next_ip = ( (mem[address_of_pc_on_stack  ]<<56) |
                (mem[address_of_pc_on_stack+1]<<48) |
                (mem[address_of_pc_on_stack+2]<<40) |
                (mem[address_of_pc_on_stack+3]<<32) |
                (mem[address_of_pc_on_stack+4]<<24) |
                (mem[address_of_pc_on_stack+5]<<16) |
                (mem[address_of_pc_on_stack+6]<<8)  |
                (mem[address_of_pc_on_stack+7]) )

    # Clear Stack Values
    (mem[address_of_pc_on_stack], mem[address_of_pc_on_stack+1],
     mem[address_of_pc_on_stack+2], mem[address_of_pc_on_stack+3],
     mem[address_of_pc_on_stack+4], mem[address_of_pc_on_stack+5],
     mem[address_of_pc_on_stack+6], mem[address_of_pc_on_stack+7]) = (
         0,0,0,0, 0, 0, 0, 0)

    return next_ip

# 3 OP
CMP = nbit_optimized_dict['CMP_64']
JUMP_P = nbit_optimized_dict['JUMP_P_64']


# 1 OP immediate
JUMP_NP = nbit_optimized_dict['JUMP_NP_64']

def CALLI(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    mem_address = register_file[reg0]
    # big endian
    mem[mem_address+0] = (next_ip>>56) & 0xFF # most significant byte
    mem[mem_address+1] = (next_ip>>48) & 0xFF
    mem[mem_address+2] = (next_ip>>40) & 0xFF
    mem[mem_address+3] = (next_ip>>32) & 0xFF
    mem[mem_address+4] = (next_ip>>24) & 0xFF
    mem[mem_address+5] = (next_ip>>16) & 0xFF
    mem[mem_address+6] = (next_ip>>8) & 0xFF
    mem[mem_address+7] = next_ip & 0xFF # least significant byte

    register_file[reg0] += register_file.itemsize # Update our index

    return next_ip + raw_immediate # Update PC

def SL0I(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    register_file[reg0] = \
        (register_file[reg0]<<raw_immediate) & 0xFFFFFFFFFFFFFFFF
    return next_ip
