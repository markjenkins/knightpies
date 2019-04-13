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
from pythoncompat import print_func, gen_range

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
    for i in range(NUM_REGISTERS):
        registers.append(0)

    amount_of_ram = size

    # allocate memory, assert unsigned char is the size we think it is
    memory = array(ARRAY_TYPE_UNSIGNED_CHAR)
    assert memory.itemsize == SIZE_UNSIGNED_CHAR # 1
    for i in gen_range(size): # using gen_range because this is a big number
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
        print_func("Invalid state reached after: %d instructions" %
                   vm[PERF_COUNT],
                   file=stderr)
        print_func("%d: %s" % (place, message), file=stderr)
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
    print_func("Invalid instruction was recieved at address:%08X" %
               current_instruction[CURIP],
               file=stderr)
    print_func("After %d instructions" % vm[PERF_COUNT], file=stderr)
    print_func("Unable to execute the following instruction:\n\t%s" %
               string_unpacked_instruction(current_instruction),
               file=stderr)

    current_instruction = invalidate_instruction(current_instruction)
    vm = halt_vm(vm)

    if DEBUG:
        print_func("Computer Program has Halted", file=stderr)

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
        print_func("Executing: %s" %
                   string_unpacked_instruction(current_instruction),
                   file=stderr)
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
        print_func(
            "Computer Program has Halted\nAfter Executing %d instructions"
            % vm[PERF_COUNT],
            file=stderr)
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

EVAL_3OP_INT_TABLE_STRING = {
    0x000: "ADD",
    0x001: "ADDU",
    0x002: "SUB",
    0x003: "SUBU",
    0x004: "CMP",
    0x005: "CMPU",
    0x006: "MUL",
    0x007: "MULH",
    0x008: "MULU",
    0x009: "MULUH",
    0x00A: "DIV",
    0x00B: "MOD",
    0x00C: "DIVU",
    0x00D: "MODU",
    0x010: "MAX",
    0x011: "MAXU",
    0x012: "MIN",
    0x013: "MINU",
    0x020: "AND",
    0x021: "OR",
    0x022: "XOR",
    0x023: "NAND",
    0x024: "NOR",
    0x025: "XNOR",
    0x026: "MPQ",
    0x027: "LPQ",
    0x028: "CPQ",
    0x029: "BPQ",
    0x030: "SAL",
    0x031: "SAR",
    0x032: "SL0",
    0x033: "SR0",
    0x034: "SL1",
    0x035: "SR1",
    0x036: "ROL",
    0x037: "ROR",
    0x038: "LOADX",
    0x03A: "LOADXU8",
    0x03B: "LOADX16",
    0x03C: "LOADXU16",
    0x03D: "LOADX32",
    0x03E: "LOADXU32",
    0x048: "STOREX",
    0x049: "STOREX8",
    0x04A: "STOREX16",
    0x04B: "STOREX32",
    0x050: "CMPJUMP_G",
    0x051: "CMPJUMP_GE",
    0x052: "CMPJUMP_E",
    0x053: "CMPJUMP_NE",
    0x054: "CMPJUMP_LE",
    0x055: "CMPJUMP_L",
    0x060: "CMPJUMPU_G",
    0x061: "CMPJUMPU_GE",
    0x064: "CMPJUMPU_LE",
    0x065: "CMPJUMPU_L",
}

EVAL_3OP_INT_TABLE = dict( map(
    lookup_instruction_and_debug_str,
    EVAL_3OP_INT_TABLE_STRING.items() ) # map
) # dict

# using a dictionary type instead of set/fozenset or sets for python 2.2
# compatibility
EVAL_30P_INT_ILLEGAL = {
    0x014: None,
    0x015: None,
    0x016: None,
    0x017: None,
    0x018: None,
    0x019: None,
    0x01A: None,
    0x01B: None,
    }

def eval_N_OP_int(vm, c, n, lookup_table, illegal_table=None):
    name = "ILLEGAL_%dOP" % n
    raw_xop = c[RAW_XOP]
    if raw_xop in lookup_table:
        instruction_func, instruction_str = lookup_table[raw_xop]
        if DEBUG:
            name = instruction_str
        #elif TRACE: # TODO
        #    record_trace(instruction_str) # TODO
        instruction_func(vm, c)

    # not sure why zome XOP are matched explicitly for illegal whereas
    # others fall into default when the handling is the same
    # some explicitly illegal XOPs in eval_3OP_int probably just exist
    # to reserve them for future use
    # elif illegal_table!=None and raw_xop in illegal_table:
    #    illegal_instruction(vm, c)
    else:
        illegal_instruction(vm, c)

    if DEBUG:
        print_func(
            ("# %s" + " reg%d"*n) % ( (name,) + c[I_REGISTERS][0:n] )
        ) # print_func
    return False # Why?

def eval_4OP_Int(vm, c):
    return eval_N_OP_int(vm, c, 4, EVAL_4OP_INT_TABLE)

def eval_3OP_Int(vm, c):
    return eval_N_OP_int(vm, c, 3, EVAL_3OP_INT_TABLE, EVAL_30P_INT_ILLEGAL)

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
    print_func( "vm created %d bytes" %  len(vm[MEM]) )
    instruction = read_instruction(vm)
    print_func( "instruction opcode unpacked (0x0%s, 0x0%s)" % 
                instruction[OP] )
