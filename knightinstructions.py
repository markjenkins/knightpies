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

from array import array
from os.path import exists
from sys import stderr, exit

from constants import \
    IP, REG, MEM, HALTED, EXCEPT, PERF_COUNT, \
    TAPE1FILENAME, TAPE2FILENAME, TAPEFD, TAPEFD_I_STDIN, TAPEFD_I_STDOUT, \
    OP, RAW, CURIP, NEXTIP, RESTOF, INVALID, \
    RAW_XOP, XOP, RAW_IMMEDIATE, IMMEDIATE, I_REGISTERS, HAL_CODE, \
    CONDITION_BIT_C, CONDITION_BIT_B, CONDITION_BIT_O, \
    CONDITION_BIT_GT, CONDITION_BIT_EQ, CONDITION_BIT_LT, \
    HAL_IO_DATA_REGISTER, HAL_IO_DEVICE_REGISTER, HAL_IO_DEVICE_STDIO

from pythoncompat import write_byte, COMPAT_TRUE, COMPAT_FALSE
from knightdecodeutil import outside_of_world

BITS_PER_BYTE = 8
def prove_8_bits_per_array_byte():
    single_byte_value = 0
    # shift in 8 bits for every byte
    unsigned_byte_array = array('B')
    for i in range(BITS_PER_BYTE * unsigned_byte_array.itemsize):
        single_byte_value = (single_byte_value<<1) | 1 # shift a 1 bit in
    if unsigned_byte_array.itemsize==1:
        assert single_byte_value == 0xFF

    try:
        unsigned_byte_array.append(single_byte_value)
    except OverflowError:
    # this could only happen if 1 byte was < 8 bits
        assert COMPAT_FALSE

    try: # now we expect this to cause an overflow
        unsigned_byte_array[0]+=1
    except OverflowError:
        return COMPAT_TRUE
    return COMPAT_FALSE
assert prove_8_bits_per_array_byte()

MAX_16_SIGNED = (2**15)-1
MAX_16_UNSIGNED = (2**16)-1

def twos_complement_conversion_w_mask(input_value, mask):
    # this is a modified version of
    # https://en.wikipedia.org/wiki
    # /Two%27s_complement#Converting_from_two's_complement_representation
    return -(input_value & mask) + (input_value & ~mask)

def make_twos_complement_converter(num_bits):
    # this is a modified version of
    # https://en.wikipedia.org/wiki
    # /Two%27s_complement#Converting_from_two's_complement_representation
    mask = 2**(num_bits-1)
    def twos_complement(input_value):
        return -(input_value & mask) + (input_value & ~mask)
    return twos_complement

sixteenbit_twos_complement = make_twos_complement_converter(16)

def interpret_sixteenbits_as_signed(value):
    if value > MAX_16_SIGNED: # would value & 0x8000 be a faster sign test?
        return sixteenbit_twos_complement(value)
    else:
        return value

def interpret_nbits_as_signed(value, bits):
    mask = 2**(bits-1)
    if value > mask-1: # greater than maximum signed value
        return twos_complement_conversion_w_mask(value, mask)
    else:
        return value

def sign_extend_16bits_unsign(value):
    # see comment inside sign_extend_if_negative_and_unsign_bits
    # on why python's infinite precision of sign bits makes this work
    return value & 0xFFFF

def sign_extend_if_negative_and_unsign_bits(value, num_bits):
    mask = (1<<num_bits)-1
    assert mask == ((2**num_bits)-1)
    # take advantage of the infinite sign bit precision of negative
    # integers on python 2.2 and onward by bitwise AND "&" with an
    # appropriate bitmask. Distinction between int (precision of C long)
    # and python long (infinite precision) in python 2.2 through 2.7 isn't
    # a problem her as mask will be a long if num_bits is the number of
    # bits used by python 2 int and the bitwise AND operation will
    # automatically up promote
    # https://wiki.python.org/moin/BitwiseOperators
    return value & mask

def stuff_int_as_signed_16bit_value_into_register(
        value, register_file, regindex):
    register_file[regindex] = sign_extend_if_negative_and_unsign_bits(
        interpret_sixteenbits_as_signed(value),
        register_file.itemsize*8)

def get_instruction_size(vm, address):
    c = vm[MEM][address]
    if c==0xE0 or c==0xE1:
        return 6
    else:
        return 4

def compare_immediate_to_register_ne(register_file, reg0, raw_immediate):
    return register_file[reg0] != raw_immediate

def compare_immediate_to_register_e(register_file, reg0, raw_immediate):
    return register_file[reg0] == raw_immediate

def compare_immediate_to_register_g_unsigned(
        register_file, reg0, raw_immediate):
    return register_file[reg0] > raw_immediate

def compare_immediate_to_register_ge_unsigned(
        register_file, reg0, raw_immediate):
    return register_file[reg0] >= raw_immediate

def compare_immediate_to_register_g_signed(
        register_file, reg0, raw_immediate):
    return \
        interpret_nbits_as_signed(register_file[reg0],
                                  register_file.itemsize*8) > \
        interpret_sixteenbits_as_signed(raw_immediate)

def compare_immediate_to_register_ge_signed(
        register_file, reg0, raw_immediate):
    return \
        interpret_nbits_as_signed(register_file[reg0],
                                  register_file.itemsize*8) >= \
        interpret_sixteenbits_as_signed(raw_immediate)

def set_comparison_flags(tmp1, tmp2, registerfile, registerindex):
    if tmp1 > tmp2:
        registerfile[registerindex] = CONDITION_BIT_GT
    elif tmp1 == tmp2:
        registerfile[registerindex] = CONDITION_BIT_EQ
    else:
        registerfile[registerindex] = CONDITION_BIT_LT

def register_negative(register_file, reg0):
    # naive version
    #return 0 > interpret_nbits_as_signed(register_file.itemsize*BITS_PER_BYTE)

    # optimize by checking the sign bit
    #
    # we could do better for specific register sizes by having
    # 2**(nbits-1)-1 precomputed and just check if we're greater than that
    return register_file[reg0]>>(register_file.itemsize*BITS_PER_BYTE-1)

def register_positive(register_file, reg0):
    return not register_negative(register_file, reg0)

def writeout_bytes(mem, pointer, value, byte_count):
    outside_of_world(
        mem, pointer,
        "Writeout bytes Address_1 is outside of World")
    outside_of_world(
        mem, pointer+byte_count-1,
        "Writeout bytes Address_2 is outside of World")
    # example invocation of range, byte_count=4 (32 bits)
    # range(24, -8, -8) = [24, 16, 8, 0]
    for i, x in enumerate(range( 8*(byte_count-1), -8, -8)):
        mem[pointer+i] = (value>>x) & 0xff

def readin_bytes(mem, pointer, signed, byte_count):
    outside_of_world(mem, pointer,
                     "READIN bytes Address_1 is outside of World")
    outside_of_world(mem, pointer+byte_count-1,
                     "READIN bytes Address_2 is outside of World")

    sign_bit = signed and mem[pointer] & 0x80
    value_sum = mem[pointer]
    for i in range(pointer+1, pointer+byte_count):
        value_sum = (value_sum<<8) + mem[i]

    if sign_bit:
        return twos_complement_conversion_w_mask(value_sum, 2**(byte_count*8-1))
    else:
        return value_sum

# 4 OP integer instructions

def get_args_for_4OP(vm, c):
    return (vm[MEM],
            vm[REG],
            c[I_REGISTERS][0], c[I_REGISTERS][1],
            c[I_REGISTERS][2], c[I_REGISTERS][3],
            c[NEXTIP])

def ADD_CI(vm, c):
    pass

def ADD_CO(vm, c):
    pass

def ADD_CIO(vm, c):
    pass

def ADDU_CI(vm, c):
    pass

def ADDU_CO(vm, c):
    pass

def ADDU_CIO(vm, c):
    pass

def SUB_BI(vm, c):
    pass

def SUB_BO(vm, c):
    pass

def SUB_BIO(vm, c):
    pass

def SUBU_BI(vm, c):
    pass

def SUBU_BO(vm, c):
    pass

def SUBU_BIO(vm, c):
    pass

def MULTIPLY(vm, c):
    pass

def MULTIPLYU(vm, c):
    pass

def DIVIDE(vm, c):
    pass

def DIVIDEU(vm, c):
    pass

def MUX(vm, c):
    mem, registerfile, reg0, reg1, reg2, reg3, next_ip = \
        get_args_for_4OP(vm, c)
    registerfile[reg0] = (
        ( registerfile[reg2] & ~(registerfile[reg1]) ) |
	( registerfile[reg3] & registerfile[reg1] )
    )
    return next_ip

def NMUX(vm, c):
    pass

def SORT(vm, c):
    pass

def SORTU(vm, c):
    pass


# 3 OP integer instructions

def get_args_for_3OP(vm, c):
    return (vm[MEM],
            vm[REG],
            c[I_REGISTERS][0], c[I_REGISTERS][1], c[I_REGISTERS][2],
            c[NEXTIP])

def ADDU(vm, c):
    mem, registerfile, reg0, reg1, reg2, next_ip = get_args_for_3OP(vm, c)
    mask = (1<<(registerfile.itemsize*8)) -1
    assert(mask == (2**(registerfile.itemsize*8))-1 )
    registerfile[reg0] = (registerfile[reg1] + registerfile[reg2]) & mask

    return next_ip

# for ADD, vm_instructions.c worries about values being signed and
# stuff, but I think the idea of twos complement integers is that stuff
# gets sorted out when we do addition and we just have to mask out the
# overflow bits (which ADDU does anyway because we need to fit in the
# destination register)
# testing needed to validate
ADD = ADDU

def SUB(vm, c):
    mem, registerfile, reg0, reg1, reg2, next_ip = get_args_for_3OP(vm, c)
    N_BITS = registerfile.itemsize*BITS_PER_BYTE
    mask = (1<<N_BITS)-1
    tmp1 = interpret_nbits_as_signed(registerfile[reg1], N_BITS)
    tmp2 = interpret_nbits_as_signed(registerfile[reg2], N_BITS)
    registerfile[reg0] = (tmp1-tmp2) & mask
    return next_ip

def SUBU(vm, c):
    pass

def CMP(vm, c):
    mem, registerfile, reg0, reg1, reg2, next_ip = get_args_for_3OP(vm, c)
    N_BITS = registerfile.itemsize*BITS_PER_BYTE
    tmp1 = interpret_nbits_as_signed(registerfile[reg1], N_BITS)
    tmp2 = interpret_nbits_as_signed(registerfile[reg2], N_BITS)
    set_comparison_flags(tmp1, tmp2, registerfile, reg0)
    return next_ip

def CMPU(vm, c):
    mem, registerfile, reg0, reg1, reg2, next_ip = get_args_for_3OP(vm, c)
    set_comparison_flags(
        registerfile[reg1], registerfile[reg2], registerfile, reg0)
    return next_ip

def MUL(vm, c):
    pass

def MULH(vm, c):
    pass

def MULU(vm, c):
    pass

def MULUH(vm, c):
    pass

def DIV(vm, c):
    pass

def MOD(vm, c):
    pass

def DIVU(vm, c):
    pass

def MODU(vm, c):
    pass

def MAX(vm, c):
    pass

def MAXU(vm, c):
    pass

def MIN(vm, c):
    pass

def MINU(vm, c):
    pass

def AND(vm, c):
    mem, registerfile, reg0, reg1, reg2, next_ip = get_args_for_3OP(vm, c)
    registerfile[reg0] = registerfile[reg1] & registerfile[reg2]
    return next_ip

def OR(vm, c):
    pass

def XOR(vm, c):
    pass

def NAND(vm, c):
    pass

def NOR(vm, c):
    pass

def XNOR(vm, c):
    pass

def MPQ(vm, c):
    pass

def LPQ(vm, c):
    pass

def CPQ(vm, c):
    pass

def BPQ(vm, c):
    pass

def SAL(vm, c):
    pass

def SAR(vm, c):
    pass

def SL0(vm, c):
    mem, registerfile, reg0, reg1, reg2, next_ip = get_args_for_3OP(vm, c)
    mask = (1<<(registerfile.itemsize*8)) -1
    registerfile[reg0] = (registerfile[reg1]<<registerfile[reg2]) & mask
    return next_ip

def SR0(vm, c):
    pass

def SL1(vm, c):
    pass

def SR1(vm, c):
    pass

def ROL(vm, c):
    pass

def ROR(vm, c):
    pass

def LOADX(vm, c):
    mem, register_file, reg0, reg1, reg2, next_ip = get_args_for_3OP(vm, c)
    register_file[reg0] = \
        readin_bytes(mem, register_file[reg1] + register_file[reg2],
                     COMPAT_TRUE, register_file.itemsize)
    return next_ip

def LOADXU8(vm, c):
    mem, register_file, reg0, reg1, reg2, next_ip = get_args_for_3OP(vm, c)
    register_file[reg0] = \
        readin_bytes(mem, register_file[reg1] + register_file[reg2],
                     COMPAT_FALSE, 1)
    return next_ip

def LOADX16(vm, c):
    pass

def LOADXU16(vm, c):
    mem, register_file, reg0, reg1, reg2, next_ip = get_args_for_3OP(vm, c)
    register_file[reg0] = \
        readin_bytes(mem, register_file[reg1] + register_file[reg2],
                     COMPAT_FALSE, 2)
    return next_ip

def LOADX32(vm, c):
    pass

def LOADXU32(vm, c):
    pass

def STOREX(vm, c):
    mem, register_file, reg0, reg1, reg2, next_ip = get_args_for_3OP(vm, c)
    writeout_bytes(mem,
                   register_file[reg1]+register_file[reg2],
                   register_file[reg0],
                   register_file.itemsize)
    return next_ip

def STOREX8(vm, c):
    pass

def STOREX16(vm, c):
    mem, register_file, reg0, reg1, reg2, next_ip = get_args_for_3OP(vm, c)
    writeout_bytes(mem,
                   register_file[reg1]+register_file[reg2],
                   register_file[reg0],
                   2)
    return next_ip

def STOREX32(vm, c):
    pass

def CMPJUMP_G(vm, c):
    pass

def CMPJUMP_GE(vm, c):
    pass

def CMPJUMP_E(vm, c):
    pass

def CMPJUMP_NE(vm, c):
    pass

def CMPJUMP_LE(vm, c):
    pass

def CMPJUMP_L(vm, c):
    pass

def CMPJUMPU_G(vm, c):
    pass

def CMPJUMPU_GE(vm, c):
    pass

def CMPJUMPU_LE(vm, c):
    pass

def CMPJUMPU_L(vm, c):
    pass


# 2 OP integer instructions

def get_args_for_2OP(vm, c):
    return vm[MEM], vm[REG], c[I_REGISTERS][0], c[I_REGISTERS][1], c[NEXTIP]

def NEG(vm, c):
    pass

def ABS(vm, c):
    pass

def NABS(vm, c):
    pass

def SWAP(vm, c):
    mem, register_file, reg0, reg1, next_ip = get_args_for_2OP(vm, c)
    utmp1 = register_file[reg1]
    register_file[reg1] = register_file[reg0]
    register_file[reg0] = utmp1
    return next_ip

def COPY(vm, c):
    mem, register_file, reg0, reg1, next_ip = get_args_for_2OP(vm, c)
    register_file[reg0] = register_file[reg1]
    return next_ip

def MOVE(vm, c):
    mem, register_file, reg0, reg1, next_ip = get_args_for_2OP(vm, c)
    register_file[reg0] = register_file[reg1]
    register_file[reg1] = 0
    return next_ip

def NOT(vm, c):
    mem, register_file, reg0, reg1, next_ip = get_args_for_2OP(vm, c)
    mask = (1<<(register_file.itemsize*8)) -1
    register_file[reg0] = (~register_file[reg1]) & mask
    return next_ip

def BRANCH(vm, c):
    pass

def CALL(vm, c):
    pass

def PUSHR(vm, c):
    mem, register_file, reg0, reg1, next_ip = get_args_for_2OP(vm, c)
    reg_size = register_file.itemsize
    writeout_bytes(mem, register_file[reg1], register_file[reg0], reg_size)
    register_file[reg1] += reg_size
    return next_ip

def PUSH8(vm, c):
    pass

def PUSH16(vm, c):
    pass

def PUSH32(vm, c):
    pass

def POPR(vm, c):
    mem, register_file, reg0, reg1, next_ip = get_args_for_2OP(vm, c)
    reg_size = register_file.itemsize
    register_file[reg1] -= reg_size
    tmp = readin_bytes(mem, register_file[reg1], COMPAT_FALSE, reg_size)
    writeout_bytes(mem, register_file[reg1], 0, reg_size)
    register_file[reg0] = tmp
    return next_ip

def POP8(vm, c):
    pass

def POPU8(vm, c):
    pass

def POP16(vm, c):
    pass

def POPU16(vm, c):
    pass

def POP32(vm, c):
    pass

def POPU32(vm, c):
    pass

def CMPSKIP_G(vm, c):
    pass

def CMPSKIP_GE(vm, c):
    pass

def CMPSKIP_E(vm, c):
    pass

def CMPSKIP_NE(vm, c):
    pass

def CMPSKIP_LE(vm, c):
    pass

def CMPSKIP_L(vm, c):
    pass

def CMPSKIPU_G(vm, c):
    pass

def CMPSKIPU_GE(vm, c):
    pass

def CMPSKIPU_LE(vm, c):
    pass

def CMPSKIPU_L(vm, c):
    pass


# 1 OP integer instructions

def get_args_for_1OP(vm, c):
    return vm[MEM], vm[REG], c[I_REGISTERS][0], c[NEXTIP]

def READPC(vm, c):
    pass

READSCID_TABLE = {
    32: 5, # 256//8
    16: 4, # 128//8
    8:  3, #  64//8
    4:  2, #  32//8
}
READSCID_DEFAULT = 1

def READSCID(vm, c):
    mem, register_file, reg0, next_ip = get_args_for_1OP(vm, c)
    register_file[reg0] = READSCID_TABLE.get(
        register_file.itemsize, READSCID_DEFAULT)
    return next_ip

def FALSE(vm, c):
    mem, register_file, reg0, next_ip = get_args_for_1OP(vm, c)
    register_file[reg0] = 0
    return next_ip

def TRUE(vm, c):
    # Don't sweat the inefficiency of calculating the maximum value for the
    # register size, seperate implementations exist in
    # knightinstructions64, knightinstructions32, knightinstructions16
    mem, register_file, reg0, next_ip = get_args_for_1OP(vm, c)
    register_file[reg0] = 2**(vm[REG].itemsize*BITS_PER_BYTE)-1
    return next_ip

def JSR_COROUTINE(vm, c):
    mem, register_file, reg0, next_ip = get_args_for_1OP(vm, c)
    return register_file[reg0]

def RET(vm, c):
    mem, register_file, reg0, next_ip_discard = get_args_for_1OP(vm, c)
    reg_size = register_file.itemsize

    # Update our index
    address_of_pc_on_stack = register_file[reg0] - reg_size
    register_file[reg0] = address_of_pc_on_stack

    # Read in the new PC
    next_ip = readin_bytes(mem, address_of_pc_on_stack, COMPAT_FALSE, reg_size)

    # Clear Stack Values
    writeout_bytes(mem, address_of_pc_on_stack, 0, reg_size)

    return next_ip

def PUSHPC(vm, c):
    pass

def POPPC(vm, c):
    pass


# 2 OP integer immediate

def get_args_for_2OPI(vm, c):
    return (vm[MEM], vm[REG],
            c[I_REGISTERS][0], c[I_REGISTERS][1],
            c[RAW_IMMEDIATE], c[NEXTIP],
            )

def ADDI(vm, c):
    pass

def ADDUI(vm, c):
    mem, register_file, reg0, reg1, raw_immediate, next_ip = \
        get_args_for_2OPI(vm, c)
    mask = (1<<(register_file.itemsize*8))-1
    register_file[reg0] = (register_file[reg1] + raw_immediate) & mask
    return next_ip

def SUBI(vm, c):
    pass

def SUBUI(vm, c):
    mem, register_file, reg0, reg1, raw_immediate, next_ip = \
        get_args_for_2OPI(vm, c)
    # subtract and use a bitmask for register_file.itemsize*8 bits
    # to match the register size. A negative result from the subtraction
    # is no problem as negative numbers of type long (2.x) or int (3.x)
    # have infinite 1 bits available for bitwise operations
    # https://wiki.python.org/moin/BitwiseOperators
    # in python 2.2-2.7 the graduation from int (precision of c long type) to
    # infinite precision long happens automatically as the mask
    # operand that will force up promotion when register_file.itemsize matches
    # the c long
    mask = (1<<(register_file.itemsize*8))-1
    assert(mask == ( (2**(register_file.itemsize*8)) -1 ))
    register_file[reg0] = (register_file[reg1] - raw_immediate) & mask
    return next_ip

def CMPI(vm, c):
    pass

def LOAD(vm, c):
    mem, register_file, reg0, reg1, raw_immediate, next_ip = \
        get_args_for_2OPI(vm, c)
    register_file[reg0] = \
        readin_bytes(mem, register_file[reg1] + raw_immediate,
                     COMPAT_FALSE, register_file.itemsize)
    return next_ip

def LOAD8(vm, c):
    pass

def LOADU8(vm, c):
    pass

def LOAD16(vm, c):
    pass

def LOADU16(vm, c):
    pass

def LOAD32(vm, c):
    pass

def LOADU32(vm, c):
    pass

def CMPUI(vm, c):
    mem, register_file, reg0, reg1, raw_immediate, next_ip = \
        get_args_for_2OPI(vm, c)
    set_comparison_flags(
        register_file[reg1], raw_immediate, register_file, reg0)
    return next_ip

def STORE(vm, c):
    mem, register_file, reg0, reg1, raw_immediate, next_ip = \
        get_args_for_2OPI(vm, c)
    writeout_bytes(mem,
                   register_file[reg1]+raw_immediate,
                   register_file[reg0],
                   register_file.itemsize)
    return next_ip

def STORE8(vm, c):
    mem, register_file, reg0, reg1, raw_immediate, next_ip = \
        get_args_for_2OPI(vm, c)
    writeout_bytes(mem, register_file[reg1] + raw_immediate,
                   register_file[reg0], 1);
    return next_ip

def STORE16(vm, c):
    pass

def STORE32(vm, c):
    pass

def ANDI(vm, c):
    mem, register_file, reg0, reg1, raw_immediate, next_ip = \
        get_args_for_2OPI(vm, c)
    register_file[reg0] = register_file[reg1] & raw_immediate
    return next_ip

def ORI(vm, c):
    pass

def XORI(vm, c):
    pass

def NANDI(vm, c):
    pass

def NORI(vm, c):
    pass

def XNORI(vm, c):
    pass

def CMPJUMPI_G(vm, c):
    pass

def CMPJUMPI_GE(vm, c):
    pass

def CMPJUMPI_E(vm, c):
    pass

def CMPJUMPI_NE(vm, c):
    pass

def CMPJUMPI_LE(vm, c):
    pass

def CMPJUMPI_L(vm, c):
    pass

def CMPJUMPUI_G(vm, c):
    pass

def CMPJUMPUI_GE(vm, c):
    pass

def CMPJUMPUI_LE(vm, c):
    pass

def CMPJUMPUI_L(vm, c):
    pass


# 1 OP integer immediate

def get_args_for_1OPI(vm, c):
    return vm[MEM], vm[REG], c[I_REGISTERS][0], c[RAW_IMMEDIATE], c[NEXTIP]

def make_condition_bit_jump(condition_mask):
    def JUMP_condition(vm, c):
        mem, register_file, reg0, raw_immediate, next_ip = \
            get_args_for_1OPI(vm, c)
        if register_file[reg0] & condition_mask:
            return next_ip + interpret_sixteenbits_as_signed(raw_immediate)
        else:
            return next_ip
    return JUMP_condition

JUMP_C = make_condition_bit_jump(CONDITION_BIT_C)
JUMP_B = make_condition_bit_jump(CONDITION_BIT_B)
JUMP_O = make_condition_bit_jump(CONDITION_BIT_O)
JUMP_G = make_condition_bit_jump(CONDITION_BIT_GT)
JUMP_E = make_condition_bit_jump(CONDITION_BIT_EQ)
JUMP_L = make_condition_bit_jump(CONDITION_BIT_LT)

def make_two_either_condition_bit_jump(condition_mask1, condition_mask2):
    combined_mask = condition_mask1 | condition_mask2
    def JUMP_two_condition(vm, c):
        mem, register_file, reg0, raw_immediate, next_ip = \
            get_args_for_1OPI(vm, c)
        # how vm_instructions.c (stage0) does this
        # if (register_file[reg0] & condition_mask1 or
        #     register_file[reg0] & condition_mask2):
        #     return next_ip + interpret_sixteenbits_as_signed(raw_immediate)
        # else:
        #     return next_ip

        # I haven't tested it, but I assume this is faster?
        if register_file[reg0] & combined_mask:
            return next_ip + interpret_sixteenbits_as_signed(raw_immediate)
        else:
            return next_ip
    return JUMP_two_condition

JUMP_GE = make_two_either_condition_bit_jump(CONDITION_BIT_GT, CONDITION_BIT_EQ)
JUMP_LE = make_two_either_condition_bit_jump(CONDITION_BIT_LT, CONDITION_BIT_EQ)

def JUMP_NE(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = \
        get_args_for_1OPI(vm, c)
    if register_file[reg0] & CONDITION_BIT_EQ:
        return next_ip
    else: # CONDITION_BIT_EQ not set
        return next_ip + interpret_sixteenbits_as_signed(raw_immediate)

def JUMP_Z(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    if 0==register_file[reg0]:
        return next_ip + interpret_sixteenbits_as_signed(raw_immediate)
    else:
        return next_ip

def JUMP_NZ(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    if 0!=register_file[reg0]:
        return next_ip + interpret_sixteenbits_as_signed(raw_immediate)
    else:
        return next_ip

def JUMP_P(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    if register_negative(register_file, reg0):
        return next_ip
    else:
        return next_ip + interpret_sixteenbits_as_signed(raw_immediate)

def JUMP_NP(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    if register_negative(register_file, reg0):
        return next_ip + interpret_sixteenbits_as_signed(raw_immediate)
    else:
        return next_ip

def CALLI(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    reg_size = register_file.itemsize
    # Write out the PC
    writeout_bytes(mem, register_file[reg0], next_ip, reg_size)

    register_file[reg0] += reg_size # Update our index

    return next_ip + interpret_sixteenbits_as_signed(raw_immediate) # Update PC

def LOADI(vm, c):
    # 16 bit version just uses LOADUI
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    stuff_int_as_signed_16bit_value_into_register(
        raw_immediate, register_file, reg0)
    return next_ip

def LOADUI(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    register_file[reg0] = raw_immediate
    return next_ip

def SALI(vm, c):
    pass

def SARI(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    register_file[reg0] = register_file[reg0]>>raw_immediate
    return next_ip

def SL0I(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    mask = (1<<(register_file.itemsize*8))-1 # (2**itemsize*8)-1, max unsigned
    assert( (2**(register_file.itemsize*8))-1 == mask )
    
    register_file[reg0] = (register_file[reg0]<<raw_immediate) & mask

    return next_ip

def SR0I(vm, c):
    pass

def SL1I(vm, c):
    pass

def SR1I(vm, c):
    pass

def LOADR(vm, c):
    pass

def LOADR8(vm, c):
    pass

def LOADRU8(vm, c):
    pass

def LOADR16(vm, c):
    pass

def LOADRU16(vm, c):
    pass

def LOADR32(vm, c):
    pass

def LOADRU32(vm, c):
    pass

def STORER(vm, c):
    pass

def STORER8(vm, c):
    pass

def STORER16(vm, c):
    pass

def STORER32(vm, c):
    pass

def CMPSKIPI_G(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    if compare_immediate_to_register_g_signed(
            register_file, reg0, raw_immediate):
        return next_ip + get_instruction_size(vm, next_ip)
    else:
        return next_ip

def CMPSKIPI_GE(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    if compare_immediate_to_register_ge_signed(
            register_file, reg0, raw_immediate):
        return next_ip + get_instruction_size(vm, next_ip)
    else:
        return next_ip

def CMPSKIPI_E(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    if compare_immediate_to_register_e(register_file, reg0, raw_immediate):
        return next_ip + get_instruction_size(vm, next_ip)
    else:
        return next_ip

def CMPSKIPI_NE(vm, c):
    mem, register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    if compare_immediate_to_register_ne(register_file, reg0, raw_immediate):
        return next_ip + get_instruction_size(vm, next_ip)
    else:
        return next_ip

def CMPSKIPI_LE(vm, c):
    pass

def CMPSKIPI_L(vm, c):
    pass

def CMPSKIPUI_G(vm, c):
    pass

def CMPSKIPUI_GE(vm, c):
    pass

def CMPSKIPUI_LE(vm, c):
    pass

def CMPSKIPUI_L(vm, c):
    pass


# 0 OP integer immediate

def JUMP(vm, c):
    return c[NEXTIP]+interpret_sixteenbits_as_signed(c[RAW_IMMEDIATE])


# HAL_CODES

def lookup_tapeindex_and_filename(vm, io_device_register=0):
    io_device = vm[REG][io_device_register]
    if 0x00001100 == io_device:
        return 0, TAPE1FILENAME, io_device
    elif 0x00001101 == io_device:
        return 1, TAPE2FILENAME, io_device
    elif HAL_IO_DEVICE_STDIO == io_device:
        return None, None, io_device
    else:
        return None, None, None

def lookup_fd(vm, io_device_register=0, write_context=COMPAT_FALSE):
    tapeindex, tapefilenameindex, io_device = lookup_tapeindex_and_filename(
        vm, io_device_register=io_device_register)
    if None==tapeindex and io_device==HAL_IO_DEVICE_STDIO:
        if write_context:
            return vm[TAPEFD][TAPEFD_I_STDOUT]
        else:
            return vm[TAPEFD][TAPEFD_I_STDIN]
    elif not (None in (tapeindex, tapefilenameindex)):
        return vm[TAPEFD][tapeindex]
    else:
        exit("Error looking up relevant tape device")

def tapeopen(vm, flags, do_exists=COMPAT_FALSE):
    tapeindex, tapefilenameindex, io_device = lookup_tapeindex_and_filename(vm)
    if None in (tapeindex, tapefilenameindex):
        exit("no tape device selected for read/write")
    filename = vm[tapefilenameindex]
    if do_exists:
        if not exists(filename):
            exit("File named %s does not exist -- python-tapeopen" %  filename)
    vm[TAPEFD][tapeindex] = open(filename, flags)

def vm_FOPEN_READ(vm):
    tapeopen(vm, 'rb', do_exists=COMPAT_TRUE)

def vm_FOPEN_WRITE(vm):
    tapeopen(vm, 'wb')

def vm_FCLOSE(vm):
    lookup_fd(vm).close()

def vm_REWIND(vm):
    lookup_fd(vm).seek(0)

def vm_FSEEK(vm):
    SEEK_CUR = 1 # wence=1 means relative to current pos 
    lookup_fd(vm).seek(VM[REG][HAL_IO_DEVICE_REGISTER], wence=SEEK_CUR)

def vm_FGETC(vm):
    byte_read = lookup_fd(
        vm, write_context=COMPAT_FALSE,
        io_device_register=HAL_IO_DEVICE_REGISTER).read(1)
    if len(byte_read)==0:
        vm[REG][HAL_IO_DATA_REGISTER] = \
            sign_extend_if_negative_and_unsign_bits(-1, vm[REG].itemsize*8)
        assert register_negative(vm[REG], HAL_IO_DATA_REGISTER)
    else:
        assert(len(byte_read)==1)
        vm[REG][HAL_IO_DATA_REGISTER] = ord(byte_read)

def vm_FPUTC(vm):
    output_byte = vm[REG][HAL_IO_DATA_REGISTER] & 0xFF
    fd = lookup_fd(
        vm, write_context=COMPAT_TRUE,
        io_device_register=HAL_IO_DEVICE_REGISTER)
    write_byte(fd, output_byte)

def vm_HAL_MEM(vm):
    pass
