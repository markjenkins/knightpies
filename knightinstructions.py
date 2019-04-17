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

from constants import \
    IP, REG, MEM, HALTED, EXCEPT, PERF_COUNT, \
    OP, RAW, CURIP, NEXTIP, RESTOF, INVALID, \
    RAW_XOP, XOP, RAW_IMMEDIATE, IMMEDIATE, I_REGISTERS, HAL_CODE

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
        assert False

    try: # now we expect this to cause an overflow
        unsigned_byte_array[0]+=1
    except OverflowError:
        return True
    return False
assert prove_8_bits_per_array_byte()

MAX_16_SIGNED = 2**15-1
MAX_16_UNSIGNED = 2**16-1
MAX_32_UNSIGNED = 2**32-1
MAX_64_UNSIGNED = 2**64-1

def make_twos_complement_converter(num_bits):
    # this is a modified version of
    # https://en.wikipedia.org/wiki
    # /Two%27s_complement#Converting_from_two's_complement_representation
    mask = 2**(num_bits-1)
    def twos_complement(input_value):
        return -(input_value & mask) + (input_value & ~mask)
    return twos_complement

sixteenbit_twos_complement = make_twos_complement_converter(16)
thirtytwobit_twos_complement = make_twos_complement_converter(32)

def interpret_sixteenbits_as_signed(value):
    if value > MAX_16_SIGNED:
        return sixteenbit_twos_complement(value)
    else:
        return value

def sign_extend_negative_and_unsign(
        value, num_bytes=None, num_bits=None, origin_bits=16):
    assert not (num_bytes==None and num_bits==None)
    assert value < 0
    if num_bytes!=None: # num_bits==None
        num_bits = num_bytes*BITS_PER_BYTE
    MAX_VALUE = 2**num_bits-1
    return_value = MAX_VALUE + value + 1
    assert 0<=return_value  <= MAX_VALUE
    return return_value

def stuff_int_as_signed_16bit_value_into_register(
        value, register_file, regindex):
    # value is currently in its unsigned form
    assert 0 <= value <= MAX_16_UNSIGNED
    register_size_bytes = register_file.itemsize
    # no conversion necessary if we're using 16 bit registers or the value
    # is positive
    if register_size_bytes==2 or 0<=value<=MAX_16_SIGNED:
        register_file[regindex] = value
    else:
        sixteenbit_signed = interpret_sixteenbits_as_signed(value)
        value_unsigned_and_signextended = \
            sign_extend_negative_and_unsign(
                sixteenbit_signed, num_bytes=register_file.itemsize )
        register_file[regindex] = value_unsigned_and_signextended

# 4 OP integer instructions

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
    pass

def NMUX(vm, c):
    pass

def SORT(vm, c):
    pass

def SORTU(vm, c):
    pass


# 3 OP integer instructions

def ADD(vm, c):
    pass

def ADDU(vm, c):
    pass

def SUB(vm, c):
    pass

def SUBU(vm, c):
    pass

def CMP(vm, c):
    pass

def CMPU(vm, c):
    pass

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
    pass

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
    pass

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
    pass

def LOADXU8(vm, c):
    pass

def LOADX16(vm, c):
    pass

def LOADXU16(vm, c):
    pass

def LOADX32(vm, c):
    pass

def LOADXU32(vm, c):
    pass

def STOREX(vm, c):
    pass

def STOREX8(vm, c):
    pass

def STOREX16(vm, c):
    pass

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

def NEG(vm, c):
    pass

def ABS(vm, c):
    pass

def NABS(vm, c):
    pass

def SWAP(vm, c):
    pass

def COPY(vm, c):
    pass

def MOVE(vm, c):
    pass

def NOT(vm, c):
    pass

def BRANCH(vm, c):
    pass

def CALL(vm, c):
    pass

def PUSHR(vm, c):
    pass

def PUSH8(vm, c):
    pass

def PUSH16(vm, c):
    pass

def PUSH32(vm, c):
    pass

def POPR(vm, c):
    pass

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
    return vm[REG], c[I_REGISTERS][0], c[NEXTIP]

def READPC(vm, c):
    pass

def READSCID(vm, c):
    pass

def FALSE(vm, c):
    register_file, reg0, next_ip = get_args_for_1OP(vm, c)
    register_file[reg0] = 0
    return next_ip

def TRUE(vm, c):
    register_file, reg0, next_ip = get_args_for_1OP(vm, c)
    register_file[reg0] = 2**(vm[REG].itemsize*BITS_PER_BYTE)-1
    return next_ip

def JSR_COROUTINE(vm, c):
    pass

def RET(vm, c):
    pass

def PUSHPC(vm, c):
    pass

def POPPC(vm, c):
    pass


# 2 OP integer immediate

def ADDI(vm, c):
    pass

def ADDUI(vm, c):
    pass

def SUBI(vm, c):
    pass

def SUBUI(vm, c):
    pass

def CMPI(vm, c):
    pass

def LOAD(vm, c):
    pass

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
    pass

def STORE(vm, c):
    pass

def STORE8(vm, c):
    pass

def STORE16(vm, c):
    pass

def STORE32(vm, c):
    pass

def ANDI(vm, c):
    pass

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
    return vm[REG], c[I_REGISTERS][0], c[RAW_IMMEDIATE], c[NEXTIP]

def JUMP_C(vm, c):
    pass

def JUMP_B(vm, c):
    pass

def JUMP_O(vm, c):
    pass

def JUMP_G(vm, c):
    pass

def JUMP_GE(vm, c):
    pass

def JUMP_E(vm, c):
    pass

def JUMP_NE(vm, c):
    pass

def JUMP_LE(vm, c):
    pass

def JUMP_L(vm, c):
    pass

def JUMP_Z(vm, c):
    pass

def JUMP_NZ(vm, c):
    pass

def JUMP_P(vm, c):
    pass

def JUMP_NP(vm, c):
    pass

def CALLI(vm, c):
    pass

def LOADI(vm, c):
    register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    stuff_int_as_signed_16bit_value_into_register(
        raw_immediate, register_file, reg0)
    return next_ip

def LOADUI(vm, c):
    register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
    register_file[reg0] = raw_immediate
    return next_ip

def SALI(vm, c):
    pass

def SARI(vm, c):
    pass

def SL0I(vm, c):
    pass

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
    pass

def CMPSKIPI_GE(vm, c):
    pass

def CMPSKIPI_E(vm, c):
    pass

def CMPSKIPI_NE(vm, c):
    pass

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
    pass


# HAL_CODES

def vm_FOPEN_READ(vm, c):
    pass

def vm_FOPEN_WRITE(vm, c):
    pass

def vm_FCLOSE(vm, c):
    pass

def vm_REWIND(vm, c):
    pass

def vm_FSEEK(vm, c):
    pass

def vm_FGETC(vm, c):
    pass

def vm_FPUTC(vm, c):
    pass

def vm_HAL_MEM(vm, c):
    pass
