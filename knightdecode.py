#!/usr/bin/env python2
#
# A derivitive port of:
# https://github.com/oriansj/stage0/blob/master/vm_decode.c
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

from array import array

ARRAY_TYPE_UNSIGNED_CHAR = 'B'
ARRAY_TYPE_UNSIGNED_SHORT = 'H'
NUM_REGISTERS = 16

SIZE_UNSIGNED_CHAR = 1
SIZE_UNSIGNED_SHORT = 2

INSTRUCTION_LEN = 4

(IP, REG, MEM, HALTED, EXCEPT, PERF_COUNT) = range(6)
(OP, CURIP, NEXTIP, RESTOF) = range(4)


def create_vm(size):
    instruction_pointer = 0

    # allocate registers, assert unsigned short is the size we think it is
    registers = array(ARRAY_TYPE_UNSIGNED_SHORT)
    assert registers.itemsize == SIZE_UNSIGNED_SHORT # 2
    for i in xrange(NUM_REGISTERS):
        registers.append(0)

    amount_of_ram = size

    # allocate memory, assert unsigned char is the size we think it is
    memory = array(ARRAY_TYPE_UNSIGNED_CHAR)
    assert memory.itemsize == SIZE_UNSIGNED_CHAR # 1
    for i in xrange(size):
        memory.append(0)

    halted = False
    exception = False
    performance_counter = 0
    
    return (instruction_pointer, registers, memory,
            halted, exception, performance_counter)

def unpack_byte(a):
    table = [0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39,
             0x41, 0x42, 0x43, 0x44, 0x45, 0x46]
    assert len(table)==16
    return (table[a / 16], table[a % 16])

def read_instruction(vm):
    current_ip = vm[IP]
    
    instruction_bytes = vm[MEM][current_ip:current_ip+INSTRUCTION_LEN]
    opcode = unpack_byte(instruction_bytes[0])

    return (opcode, # OP
            current_ip, # CURIP
            current_ip+INSTRUCTION_LEN, # NEXTIP
            [unpack_byte(a) for a in instruction_bytes[1:]] # RESTOF
    )
    
if __name__ == "__main__":
    vm = create_vm(2**16) # (64*1024)
    print "vm created %d bytes" %  len(vm[MEM])
    print "instruction opcode unpacked (0x%02x, 0x%02x)" % \
        read_instruction(vm)[OP]
