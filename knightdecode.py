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
        #     record_trance("HALT") # TODO
        #    print_traces() # TODO
    else:
        illegal_instruction(vm, current_instruction)

def decode_40P(vm, c):
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

def decode_30P(vm, c):
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

def decode_20P(vm, c):
    pass

def decode_10P(vm, c):
    pass

def decode_20PI(vm, c):
    pass

def decode_10PI(vm, c):
    pass

def decode_00PI(vm, c):
    pass

def decode_HALCODE(vm, c):
    pass

def eval_40P_Int(vm, c):
    ILLEGAL_MSG = "ILLEGAL_4OP"
    raw_xop = c[RAW_XOP]
    if raw_xop==0x00: # ADD.CI
        pass
    elif raw_xop==0x01: # ADD.CO
        pass
    elif raw_xop==0x02: # ADD.CIO
        pass
    elif raw_xop==0x03: # ADDU.CI
        pass
    elif raw_xop==0x04: # ADDU.CO
        pass
    elif raw_xop==0x05: # ADDU.CIO
        pass
    elif raw_xop==0x06: # SUB.BI
        pass
    elif raw_xop==0x07: # SUB.BO
        pass
    elif raw_xop==0x08: # SUB.BIO
        pass
    elif raw_xop==0x09: # SUBU.BI
        pass
    elif raw_xop==0x0A: # SUBU.BO
        pass
    elif raw_xop==0x0B: # SUBU.BIO
        pass
    elif raw_xop==0x0C: # MULTIPLY
        pass
    elif raw_xop==0x0D: # MULTIPLYU
        pass
    elif raw_xop==0x0E: # DIVIDE
        pass
    elif raw_xop==0x0F: # DIVIDEU
        pass
    elif raw_xop==0x10: # MUX
        pass
    elif raw_xop==0x11: # NMUX
        pass
    elif raw_xop==0x12: # SORT
        pass
    elif raw_xop==0x13: # SORTU
        pass
    else:
        illegal_instruction(vm, c)
    if DEBUG:
        print "# %s reg%d reg%d reg%d reg%d" % (
            "", # Name in original code
            ) + c[I_REGISTERS][0:4]
    return False

def eval_30P_Int(vm, c):
    pass

def eval_20P_Int(vm, c):
    pass

def eval_10P_Int(vm, c):
    pass

def eval_20PI_Int(vm, c):
    pass

def eval_Integer_10PI(vm, c):
    pass

def eval_Integer_00PI(vm, c):
    pass

def eval_HALCODE(vm, c):
    pass

DECODE_TABLE = {
    0x01: decode_40P,
    0x05: decode_30P,
    0x09: decode_20P,
    0x0D: decode_10P,
    0xE1: decode_20PI,
    0xE0: decode_10PI,
    0x3C: decode_00PI,
    0x42: decode_HALCODE,
}

EVAL_TABLE = {
    0x01: eval_40P_Int,
    0x05: eval_30P_Int,
    0x09: eval_20P_Int,
    0x0D: eval_10P_Int,
    0xE1: eval_20PI_Int,
    0xE0: eval_Integer_10PI,
    0x3C: eval_Integer_00PI,
    0x42: eval_HALCODE,
}

assert tuple(sorted(DECODE_TABLE.keys())) == tuple(sorted(EVAL_TABLE.keys()))

if __name__ == "__main__":
    vm = create_vm(2**16) # (64*1024)
    print "vm created %d bytes" %  len(vm[MEM])
    instruction = read_instruction(vm)
    print "instruction opcode unpacked (0x0%s, 0x0%s)" % \
        instruction[OP]
