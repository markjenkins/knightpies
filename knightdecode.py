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

from sys import stderr
from time import sleep
from array import array

import knightinstructions

ARRAY_TYPE_UNSIGNED_CHAR = 'B'
ARRAY_TYPE_UNSIGNED_SHORT = 'H'
NUM_REGISTERS = 16

SIZE_UNSIGNED_CHAR = 1
SIZE_UNSIGNED_SHORT = 2

INSTRUCTION_LEN = 4

DEBUG = False

EXIT_FAILURE = 1

(IP, REG, MEM, HALTED, EXCEPT, PERF_COUNT) = range(6)
(OP, RAW, CURIP, NEXTIP, RESTOF, INVALID,
 RAW_XOP, XOP, RAW_IMMEDIATE, I_REGISTERS) = range(10)


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
    table = ['0','1', '2', '3', '4', '5', '6', '7', '8', '9',
             'A', 'B', 'C', 'D', 'E', 'F']
    assert len(table)==16
    return (table[a / 16], table[a % 16])

def read_instruction(vm):
    current_ip = vm[IP]
    next_ip = current_ip+INSTRUCTION_LEN

    # Why current_ip+INSTRUCTION_LEN-1 and not just current_ip ?
    # If the end of memory isn't INSTRUCTION_LEN byte aligned, than
    # current_ip may be in bounds but the last byte of it might not be
    outside_of_world(vm, next_ip-1, "READ Instruction outside of World")
    
    instruction_bytes = vm[MEM][current_ip:current_ip+INSTRUCTION_LEN]
    opcode = unpack_byte(instruction_bytes[0])

    return (opcode, # OP
            instruction_bytes, # RAW
            current_ip, # CURIP
            next_ip, # NEXTIP
            [unpack_byte(a) for a in instruction_bytes[1:]], # RESTOF
            False # INVALID
    )

def halt_vm(vm):
    # recontruct vm tuple with vm[HALTED] = True
    return vm[0:HALTED] + (True,) + vm[HALTED+1:]

def outside_of_world(vm, place, message):
    if len(vm[MEM]) <= place:
        print >> stderr, "Invalid state reached after: %d instructions" \
            % vm[PERF_COUNT]
        print >> stderr, "%d: %s" % (place, message)
        vm = halt_vm(vm)
        # if TRACE: TODO
        #    pass # TODO
	exit(message)

def increment_vm_perf_count(vm):
    assert PERF_COUNT == len(vm)-1 # PERF_COUNT is end of the list
    return vm[0:PERF_COUNT] + (vm[PERF_COUNT]+1,)
        
def invalidate_instruction(i):
    return i[0:INVALID] + (True,) + i[INVALID+1:]

def illegal_instruction(vm, current_instruction):
    print >> stderr, \
        "Invalid instruction was recieved at address:%08X" % \
        current_instruction[CURIP]
    print >> stderr, \
        "After %d instructions" % vm[PERF_COUNT]
    print >> stderr, "Unable to execute the following instruction:\n\t%s" % \
        string_unpacked_instruction(current_instruction)

    current_instruction = invalidate_instruction(current_instruction)
    vm = halt_vm(vm)

    if DEBUG:
        print >> stderr, "Computer Program has Halted"

    #if TRACE: # TODO
    #    record_trace("HALT") # TODO
    #    print_traces() # TODO

    exit(EXIT_FAILURE)

def string_unpacked_instruction(i):
    return (''.join(i[OP]) +
            ''.join(''.join(rpair)
                    for rpair in i[RESTOF]) )

def eval_instruction(vm, current_instruction):
    vm = increment_vm_perf_count(vm)
    if DEBUG:
        print "Executing: %s" % string_unpacked_instruction(
            current_instruction)
        sleep(1)

    raw0 = current_instruction[RAW][0]
        
    if raw0 == 0: # Deal with NOPs
        if [0,0,0,0]==current_instruction[RAW].tolist():
            #if TRACE: # TODO
            #    record_trace("NOP") # TODO
            return
        illegal_instruction(vm, current_instruction)

    elif raw0 in DECODE_TABLE:
        assert raw0 in EVAL_TABLE
        current_instruction = DECODE_TABLE[raw0](current_instruction)
        EVAL_TABLE[raw0](vm, current_instruction)
    elif raw0 == 0xFF:  # Deal with HALT
        vm = halt_vm(vm)
        print >> stderr, \
            "Computer Program has Halted\nAfter Executing %d instructions" \
            % vm[PERF_COUNT]
        # if TRACE: # TODO
        #    record_trace("HALT") # TODO
        #    print_traces() # TODO
    else:
        illegal_instruction(vm, current_instruction)

def decode_4OP(vm, c):
    raw_xop = c[RAW][1]
    xop = (c[RESTOF][0], c[RESTOF][1])
    raw_immediate = 0
    i_registers = (
        c[RAW][2]/16,
        c[RAW][2]%16,
        c[RAW][3]/16,
        c[RAW][3]%16,
    )
    return c + (raw_xop, # RAW_XOP
                xop, # XOP
                raw_immediate, # RAW_IMMEDIATE
                i_registers, # I_REGISTERS
    )

def decode_3OP(vm, c):
    raw_xop = c[RAW][1]*0x10 + c[RAW][2]/16
    xop = c[RESTOF]
    assert len(xop) == 3
    raw_immediate = 0
    i_registers = (
        c[RAW][2]%16,
        c[RAW][3]/16,
        c[RAW][3]%16,
    )
    return c + (raw_xop, # RAW_XOP
                xop, # XOP
                raw_immediate, # RAW_IMMEDIATE
                i_registers, # I_REGISTERS
    )

def decode_2OP(vm, c):
    pass

def decode_1OP(vm, c):
    pass

def decode_2OPI(vm, c):
    pass

def decode_1OPI(vm, c):
    pass

def decode_0OPI(vm, c):
    pass

def decode_HALCODE(vm, c):
    pass

def lookup_instruction_and_debug_str(x):
    table_key, instruction_str = x
    return (table_key,
            (getattr(knightinstructions, instruction_str),
             instruction_str.replace("_", ".")
            ) # inner tuple
    ) # outer tuple

EVAL_4OP_INT_TABLE_STRING = {
    0x00: "ADD_CI",
    0x01: "ADD_CO",
    0x02: "ADD_CIO",
    0x03: "ADDU_CI",
    0x04: "ADDU_CO",
    0x05: "ADDU_CIO",
    0x06: "SUB_BI",
    0x07: "SUB_BO",
    0x08: "SUB_BIO",
    0x09: "SUBU_BI",
    0x0A: "SUBU_BO",
    0x0B: "SUBU_BIO",
    0x0C: "MULTIPLY",
    0x0D: "MULTIPLYU",
    0x0E: "DIVIDE",
    0x0F: "DIVIDEU",
    0x10: "MUX",
    0x11: "NMUX",
    0x12: "SORT",
    0x13: "SORTU",
}

EVAL_4OP_INT_TABLE = dict( map(
    lookup_instruction_and_debug_str,
    EVAL_4OP_INT_TABLE_STRING.items() ) # map
) # dict


def eval_4OP_Int(vm, c):
    ILLEGAL_MSG = "ILLEGAL_4OP"
    name = ILLEGAL_MSG
    raw_xop = c[RAW_XOP]
    if raw_xop in EVAL_4OP_INT_TABLE:
        instruction_func, instruction_str = EVAL_4OP_INT_TABLE[raw_xop]
        if DEBUG:
            name = instruction_str
        #elif TRACE: # TODO
        #    record_trace(instruction_str) # TODO
        instruction_func(vm, c)
    else:
        illegal_instruction(vm, c)

    if DEBUG:
        print "# %s reg%d reg%d reg%d reg%d" % (
            name,
            ) + c[I_REGISTERS][0:4]
    return False

def eval_3OP_Int(vm, c):
    pass

def eval_2OP_Int(vm, c):
    pass

def eval_1OP_Int(vm, c):
    pass

def eval_2OPI_Int(vm, c):
    pass

def eval_Integer_1OPI(vm, c):
    pass

def eval_Integer_0OPI(vm, c):
    pass

def eval_HALCODE(vm, c):
    pass

DECODE_TABLE = {
    0x01: decode_4OP,
    0x05: decode_3OP,
    0x09: decode_2OP,
    0x0D: decode_1OP,
    0xE1: decode_2OPI,
    0xE0: decode_1OPI,
    0x3C: decode_0OPI,
    0x42: decode_HALCODE,
}

EVAL_TABLE = {
    0x01: eval_4OP_Int,
    0x05: eval_3OP_Int,
    0x09: eval_2OP_Int,
    0x0D: eval_1OP_Int,
    0xE1: eval_2OPI_Int,
    0xE0: eval_Integer_1OPI,
    0x3C: eval_Integer_0OPI,
    0x42: eval_HALCODE,
}

assert tuple(sorted(DECODE_TABLE.keys())) == tuple(sorted(EVAL_TABLE.keys()))

if __name__ == "__main__":
    vm = create_vm(2**16) # (64*1024)
    print "vm created %d bytes" %  len(vm[MEM])
    instruction = read_instruction(vm)
    print "instruction opcode unpacked (0x0%s, 0x0%s)" % \
        instruction[OP]
