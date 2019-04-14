#!/usr/bin/env python
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

from __future__ import division # prevent use of "/" in the old way

from sys import stderr
from time import sleep
from array import array

import knightinstructions
from pythoncompat import print_func, gen_range
from constants import EXIT_FAILURE

ARRAY_TYPE_UNSIGNED_CHAR = 'B'
ARRAY_TYPE_UNSIGNED_SHORT = 'H'
ARRAY_TYPE_UNSIGNED_INT = 'I'
ARRAY_TYPE_UNSIGNED_INT_LONG = 'L'
NUM_REGISTERS = 16

SIZE_UNSIGNED_CHAR = 1
MIN_SIZE_UNSIGNED_SHORT = 2
MIN_SIZE_UNSIGNED_INT = 4

MIN_INSTRUCTION_LEN = 4

DEBUG = False

OUTSIDE_WORLD_ERROR = "READ Instruction outside of World"

(IP, REG, MEM, HALTED, EXCEPT, PERF_COUNT) = range(6)
(OP, RAW, CURIP, NEXTIP, RESTOF, INVALID,
 RAW_XOP, XOP, RAW_IMMEDIATE, IMMEDIATE, I_REGISTERS, HAL_CODE) = range(12)


def grow_memory(vm, size):
    while len(vm[MEM])<size:
        vm[MEM].append(0)

def create_vm(size, registersize=32):
    instruction_pointer = 0

    if registersize==32:
        registers = array(ARRAY_TYPE_UNSIGNED_INT)
        assert registers.itemsize == MIN_SIZE_UNSIGNED_INT # 4
    elif registersize==64:
        registers = array(ARRAY_TYPE_UNSIGNED_INT_LONG)
        if registers.itemsize != 64//8: # 64//8==8
            # 32 bits (4 bytes) is too small, but at least we expect to see it
            # on some platforms, so this assert will still pass
            assert registers.itemsize >= 4
            raise Exception("64 bit register size not available "
                            "on this platform")
    elif registersize==16:
        # allocate registers, assert unsigned short is the size we think it is
        registers = array(ARRAY_TYPE_UNSIGNED_SHORT)
        assert registers.itemsize == MIN_SIZE_UNSIGNED_SHORT # 2
    else:
        raise Exception("%d bit register size not available on this platform"
                        % registersize
        )
    for i in range(NUM_REGISTERS):
        registers.append(0)

    amount_of_ram = size

    # allocate memory, assert unsigned char is the size we think it is
    memory = array(ARRAY_TYPE_UNSIGNED_CHAR)
    assert memory.itemsize == SIZE_UNSIGNED_CHAR # 1


    halted = False
    exception = False
    performance_counter = 0

    vm = (instruction_pointer, registers, memory,
          halted, exception, performance_counter)
    grow_memory(vm, size)
    return vm

def unpack_byte(a):
    table = ['0','1', '2', '3', '4', '5', '6', '7', '8', '9',
             'A', 'B', 'C', 'D', 'E', 'F']
    assert len(table)==16
    return (table[a // 16], table[a % 16])

def read_instruction(vm):
    current_ip = vm[IP]
    next_ip = current_ip+MIN_INSTRUCTION_LEN

    # Why current_ip+MIN_INSTRUCTION_LEN-1 and not just current_ip ?
    # If the end of memory isn't MIN_INSTRUCTION_LEN byte aligned, than
    # current_ip may be in bounds but the last byte of it might not be
    outside_of_world(vm, next_ip-1, OUTSIDE_WORLD_ERROR)
    
    instruction_bytes = vm[MEM][current_ip:current_ip+MIN_INSTRUCTION_LEN]
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

def vm_with_new_ip(vm, new_ip):
    return vm[0:IP] + (new_ip,) + vm[IP+1:]

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
            return vm_with_new_ip(vm, current_instruction[NEXTIP])
        illegal_instruction(vm, current_instruction)

    elif raw0 in DECODE_TABLE:
        assert raw0 in EVAL_TABLE
        current_instruction = DECODE_TABLE[raw0](vm, current_instruction)
        return vm_with_new_ip(vm,
                              EVAL_TABLE[raw0](vm, current_instruction) )
    elif raw0 == 0xFF:  # Deal with HALT
        vm = halt_vm(vm)
        print_func(
            "Computer Program has Halted\nAfter Executing %d instructions"
            % vm[PERF_COUNT],
            file=stderr)
        # if TRACE: # TODO
        #    record_trace("HALT") # TODO
        #    print_traces() # TODO
        return vm
    else:
        illegal_instruction(vm, current_instruction)

    # we shouldn't make it this far, other branches call exit()
    assert False
    return None

def decode_4OP(vm, c):
    raw_xop = c[RAW][1]
    xop = (c[RESTOF][0][0], c[RESTOF][0][1])
    raw_immediate = 0
    i_registers = (
        c[RAW][2]//16,
        c[RAW][2]%16,
        c[RAW][3]//16,
        c[RAW][3]%16,
    )
    return c + (raw_xop, # RAW_XOP
                xop, # XOP
                raw_immediate, # RAW_IMMEDIATE
                (), # IMMEDIATE
                i_registers, # I_REGISTERS
                None, # HAL_CODE
    )

def decode_3OP(vm, c):
    raw_xop = c[RAW][1]*0x10 + c[RAW][2]//16
    xop = (c[RESTOF][0][0], c[RESTOF][0][1], c[RESTOF][1][0])
    assert len(xop) == 3
    raw_immediate = 0
    i_registers = (
        c[RAW][2]%16,
        c[RAW][3]//16,
        c[RAW][3]%16,
    )
    return c + (raw_xop, # RAW_XOP
                xop, # XOP
                raw_immediate, # RAW_IMMEDIATE
                (), # IMMEDIATE
                i_registers, # I_REGISTERS
                None, # HAL_CODE
    )

def decode_2OP(vm, c):
    raw_xop = c[RAW][1]*0x100 + c[RAW][2]
    xop = tuple([x
                 for x in r
                 for r in c[RESTOF][0:2] ])
    assert len(xop) == 4
    raw_immediate = 0
    i_registers = (
        c[RAW][3]//16,
        c[RAW][3]%16,
    )
    return c + (raw_xop, # RAW_XOP
                xop, # XOP
                raw_immediate, # RAW_IMMEDIATE
                (), # IMMEDIATE
                i_registers, # I_REGISTERS
                None, # HAL_CODE
    )

def decode_1OP(vm, c):
    raw_xop = c[RAW][1]*0x1000 + c[RAW][2]*0x10 + c[RAW][3]//16
    xop = tuple([x
                 for x in r
                 for r in c[RESTOF][0:2] ]) + (c[RESTOF][2][0],)
    assert len(xop) == 5
    raw_immediate = 0
    i_registers = (c[RAW][3]%16,)
    return c + (raw_xop, # RAW_XOP
                xop, # XOP
                raw_immediate, # RAW_IMMEDIATE
                (), # IMMEDIATE
                i_registers, # I_REGISTERS
                None, # HAL_CODE
    )

def decode_2OPI(vm, c):
    next_ip = c[NEXTIP]
    raw_immediate = vm[MEM][next_ip]
    next_ip+=1
    hold = vm[MEM][next_ip]
    next_ip+=1
    raw_immediate = raw_immediate*0x100 + hold
    immediate = tuple([x
                       for x in r
                       for r in c[RESTOF][1:] ] )
    assert len(immediate) == 4
    i_registers = (c[RAW][3]//16, c[RAW][3]%16)
    return c[0:NEXTIP] + (next_ip,) + c[NEXTIP+1:] + (
        None, # RAW_XOP
        None, # XOP
        raw_immediate, # RAW_IMMEDIATE
        immediate, # IMMEDIATE
        i_registers, # I_REGISTERS
        None, # HAL_CODE
    )

def decode_1OPI(vm, c):
    next_ip = c[NEXTIP]
    outside_of_world(vm, next_ip+2-1, OUTSIDE_WORLD_ERROR)
    raw_immediate = vm[MEM][next_ip]
    next_ip+=1
    hold = vm[MEM][next_ip]
    next_ip+=1
    raw_immediate = raw_immediate*0x100 + hold
    immediate = tuple([x
                       for r in c[RESTOF][1:]
                       for x in r] )
    assert len(immediate) == 4
    hal_code = 0
    raw_xop = c[RAW][3]//16
    xop = (c[RESTOF][2][1],)
    i_registers = (c[RAW][3]%16,)
    return c[0:NEXTIP] + (next_ip,) + c[NEXTIP+1:] + (
        raw_xop, # RAW_XOP
        xop,
        raw_immediate, # RAW_IMMEDIATE
        immediate, # IMMEDIATE
        i_registers, # I_REGISTERS
        hal_code, # HAL_CODE
    )

def decode_0OPI(vm, c):
    raw_immediate = c[RAW][2]*0x100 + c[RAW][3]
    immediate = tuple([x
                       for r in c[RESTOF][1:]
                       for x in r] )
    assert len(immediate)==4
    hal_code = 0
    raw_xop = c[RAW][1]
    xop = c[RESTOF][0]
    assert len(xop)==2
    return c + (
        raw_xop, # RAW_XOP
        xop, # XOP
        raw_immediate, # RAW_IMMEDIATE
        immediate, # IMMEDIATE
        (), # I_REGISTERS
        hal_code, # HAL_CODE
    )

def decode_HALCODE(vm, c):
    return c + (
        None, # RAW_XOP
        None, # XOP
        None, # RAW_IMEDIATE
        None, # IMMEDIATE
        (), # I_REGISTERS
        c[RAW][1]*0x10000 + c[RAW][2]*0x100 + c[RAW][3] # HAL_CODE
        )

def lookup_instruction_and_debug_str(x, replace_underscore=True):
    table_key, instruction_str = x
    if replace_underscore:
        instruction_str_debug = instruction_str.replace("_", ".")
    else:
        instruction_str_debug = instruction_str

    return (table_key,
            (getattr(knightinstructions, instruction_str),
             instruction_str_debug
            ) # inner tuple
    ) # outer tuple

def lookup_instruction_and_debug_str_no_sub(x):
    return lookup_instruction_and_debug_str(x, replace_underscore=False)

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

EVAL_2OP_INT_TABLE_STRING = {
    0x0000: "NEG",
    0x0001: "ABS",
    0x0002: "NABS",
    0x0003: "SWAP",
    0x0004: "COPY",
    0x0005: "MOVE",
    0x0006: "NOT",
    0x0100: "BRANCH",
    0x0101: "CALL",
    0x0200: "PUSHR",
    0x0201: "PUSH8",
    0x0202: "PUSH16",
    0x0203: "PUSH32",
    0x0280: "POPR",
    0x0281: "POP8",
    0x0282: "POPU8",
    0x0283: "POP16",
    0x0284: "POPU16",
    0x0285: "POP32",
    0x0286: "POPU32",
    0x0300: "CMPSKIP_G",
    0x0301: "CMPSKIP_GE",
    0x0302: "CMPSKIP_E",
    0x0304: "CMPSKIP_NE",
    0x0305: "CMPSKIP_LE",
    0x0305: "CMPSKIP_L",
    0x0380: "CMPSKIPU_G",
    0x0381: "CMPSKIPU_GE",
    0x0384: "CMPSKIPU_LE",
    0x0385: "CMPSKIPU_L",
    }

EVAL_2OP_INT_TABLE = dict( map(
    lookup_instruction_and_debug_str,
    EVAL_2OP_INT_TABLE_STRING.items() ) # map
) # dict

EVAL_1OP_INT_TABLE_STRING = {
    0x00000: "READPC",
    0x00001: "READSCID",
    0x00002: "FALSE",
    0x00003: "TRUE",
    0x01000: "JSR_COROUTINE",
    0x01001: "RET",
    0x02000: "PUSHPC",
    0x02001: "POPPC",
}

EVAL_1OP_INT_TABLE = dict( map(
    lookup_instruction_and_debug_str,
    EVAL_1OP_INT_TABLE_STRING.items() ) # map
) # dict

EVAL_1OP_INT_TABLE_STRING = {
    0x00000: "READPC",
    0x00001: "READSCID",
    0x00002: "FALSE",
    0x00003: "TRUE",
    0x01000: "JSR_COROUTINE",
    0x01001: "RET",
    0x02000: "PUSHPC",
    0x02001: "POPPC",
}

EVAL_1OP_INT_TABLE = dict( map(
    lookup_instruction_and_debug_str_no_sub,
    EVAL_1OP_INT_TABLE_STRING.items() ) # map
) # dict

EVAL_2OPI_INT_TABLE_STRING = {
    0x0E: "ADDI",
    0x0F: "ADDUI",
    0x10: "SUBI",
    0x11: "SUBUI",
    0x12: "CMPI",
    0x13: "LOAD",
    0x14: "LOAD8",
    0x15: "LOADU8",
    0x16: "LOAD16",
    0x17: "LOADU16",
    0x18: "LOAD32",
    0x19: "LOADU32",
    0x1F: "CMPUI",
    0x20: "STORE",
    0x21: "STORE8",
    0x22: "STORE16",
    0x23: "STORE32",
    0xB0: "ANDI",
    0xB1: "ORI",
    0xB2: "XORI",
    0xB3: "NANDI",
    0xB4: "NORI",
    0xB5: "XNORI",
    0xC0: "CMPJUMPI_G",
    0xC1: "CMPJUMPI_GE",
    0xC2: "CMPJUMPI_E",
    0xC3: "CMPJUMPI_NE",
    0xC4: "CMPJUMPI_LE",
    0xC5: "CMPJUMPI_L",
    0xD0: "CMPJUMPUI_G",
    0xD1: "CMPJUMPUI_GE",
    0xD4: "CMPJUMPUI_LE",
    0xD5: "CMPJUMPUI_L",
    }

EVAL_2OPI_INT_TABLE = dict( map(
    lookup_instruction_and_debug_str,
    EVAL_2OPI_INT_TABLE_STRING.items() ) # map
) # dict

EVAL_1OPI_INT_TABLE_STRING = {
    0x2C0: "JUMP_C",
    0x2C1: "JUMP_B",
    0x2C2: "JUMP_O",
    0x2C3: "JUMP_G",
    0x2C4: "JUMP_GE",
    0x2C5: "JUMP_E",
    0x2C6: "JUMP_NE",
    0x2C7: "JUMP_LE",
    0x2C8: "JUMP_L",
    0x2C9: "JUMP_Z",
    0x2CA: "JUMP_NZ",
    0x2CB: "JUMP_P",
    0x2CC: "JUMP_NP",
    0x2D0: "CALLI",
    0x2D1: "LOADI",
    0x2D2: "LOADUI",
    0x2D3: "SALI",
    0x2D4: "SARI",
    0x2D5: "SL0I",
    0x2D6: "SR0I",
    0x2D7: "SL1I",
    0x2D8: "SR1I",
    0x2E0: "LOADR",
    0x2E1: "LOADR8",
    0x2E2: "LOADRU8",
    0x2E3: "LOADR16",
    0x2E4: "LOADRU16",
    0x2E5: "LOADR32",
    0x2E6: "LOADRU32",
    0x2F0: "STORER",
    0x2F1: "STORER8",
    0x2F2: "STORER16",
    0x2F3: "STORER32",
    0xA00: "CMPSKIPI_G",
    0xA01: "CMPSKIPI_GE",
    0xA02: "CMPSKIPI_E",
    0xA03: "CMPSKIPI_NE",
    0xA04: "CMPSKIPI_LE",
    0xA05: "CMPSKIPI_L",
    0xA10: "CMPSKIPUI_G",
    0xA11: "CMPSKIPUI_GE",
    0xA14: "CMPSKIPUI_LE",
    0xA15: "CMPSKIPUI_L",
    }

EVAL_1OPI_INT_TABLE = dict( map(
    lookup_instruction_and_debug_str,
    EVAL_1OPI_INT_TABLE_STRING.items() ) # map
) # dict

def eval_N_OP_int(vm, c, n, lookup_val, lookup_table,
                  immediate=False, illegal_table=None):
    next_ip = None
    if immediate:
        name = "ILLEGAL_%dOPI" % n
    else:
        name = "ILLEGAL_%dOP" % n
    if lookup_val in lookup_table:
        instruction_func, instruction_str = lookup_table[lookup_val]
        if DEBUG:
            name = instruction_str
        #elif TRACE: # TODO
        #    record_trace(instruction_str) # TODO
        next_ip = instruction_func(vm, c)

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
            ("# %s" + " reg%d"*n) % ( (name,) + c[I_REGISTERS][0:n] ),
            end="",
            sep="",
        ) # print_func
        if immediate:
            print_func(" %d" % c[RAW_IMMEDIATE] )
        else:
            print_func()
    return next_ip

def eval_4OP_Int(vm, c):
    return eval_N_OP_int(vm, c, 4, c[RAW_XOP], EVAL_4OP_INT_TABLE)

def eval_3OP_Int(vm, c):
    return eval_N_OP_int(vm, c, 3,
                         c[RAW_XOP], EVAL_3OP_INT_TABLE,
                         illegal_table=EVAL_30P_INT_ILLEGAL)

def eval_2OP_Int(vm, c):
    return eval_N_OP_int(vm, c, 2, c[RAW_XOP], EVAL_2OP_INT_TABLE)

def eval_1OP_Int(vm, c):
    return eval_N_OP_int(vm, c, 1, c[RAW_XOP], EVAL_1OP_INT_TABLE)

def eval_2OPI_Int(vm, c):
    return eval_N_OP_int(vm, c, 2, c[RAW][2], EVAL_2OPI_INT_TABLE,
                         immediate=True)

def eval_Integer_1OPI(vm, c):
    return eval_N_OP_int(vm, c, 2,
                         c[RAW][2]*16 + c[RAW_XOP], EVAL_1OPI_INT_TABLE,
                         immediate=True)

def eval_Integer_0OPI(vm, c):
    next_ip = None
    name = "ILLEGAL_0OPI"
    if c[RAW_XOP] == 0x00: # JUMP
        if DEBUG:
            name = "JUMP"
        #elif TRACE: # TODO
        #    record_trace("JUMP") # TODO
        next_ip = JUMP(vm, c)
    else:
        illegal_instruction(vm, c)

    if DEBUG:
        print_func( "# %s %d\n" % (name, c[RAW_IMMEDIATE]) )
    return next_ip

HAL_CODES_TABLE_STRING = {
    0x100000: "FOPEN_READ",
    0x100001: "FOPEN_WRITE",
    0x100002: "FCLOSE",
    0x100003: "REWIND",
    0x100004: "FSEEK",
    0x100100: "FGETC",
    0x100200: "FPUTC",
    0x110000: "HAL_MEM",
    }

def hal_code_table_entry(x):
    table_key, instruction_str = x

    return (table_key,
            (getattr(knightinstructions, "vm_" + instruction_str),
             instruction_str
            ) # inner tuple
    ) # outer tuple

HAL_CODES_TABLE = dict( map( hal_code_table_entry,
                             HAL_CODES_TABLE_STRING.items() ) # map
) # dict

def eval_HALCODE(vm, c):
    next_ip = None
    name = "ILLEGAL_HALCODE"

    # POSIX MODE instructions not implemented

    if c[HAL_CODE] in HAL_CODES_TABLE:
        HAL_CODES_TABLE[c[HAL_CODE]]
        instruction_func, instruction_str = lookup_table[lookup_val]
        if DEBUG:
            name = instruction_str
        #elif TRACE: # TODO
        #    record_trace(instruction_str) # TODO
        instruction_func(vm)
        next_ip = c[NEXTIP]
    else:
        print_func("Invalid HALCODE", file=stderr)
        print_func("Computer Program has Halted", file=stderr)
        illegal_instruction(vm, c)

    if DEBUG:
        print_func("# %s" % name)
    return next_ip

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

def read_and_eval(vm):
    vm = eval_instruction(vm, read_instruction(vm))
    if vm==None or vm[IP]==None:
        assert False # this shouldn't happen
        # catch if asserts are off
        raise Exception(
            "eval_instruction did not return a new vm state")
    return vm

if __name__ == "__main__":
    vm = create_vm(2**16) # (64*1024)
    print_func( "vm created %d bytes" %  len(vm[MEM]) )
    instruction = read_instruction(vm)
    print_func( "instruction opcode unpacked (0x0%s, 0x0%s)" % 
                instruction[OP] )
