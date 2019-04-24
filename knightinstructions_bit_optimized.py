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

from knightinstructions import \
    make_twos_complement_converter, sixteenbit_twos_complement, \
    MAX_16_SIGNED, MAX_16_UNSIGNED, \
    get_args_for_1OP, get_args_for_3OP, get_args_for_1OPI

def make_nbit_optimized_functions(nbits):
    if nbits==16:
        MAX_N_SIGNED = MAX_16_SIGNED
        MAX_N_UNSIGNED = MAX_16_UNSIGNED
        nbit_twos_complement = sixteenbit_twos_complement
    else:
        MAX_N_SIGNED = 2**(nbits-1)-1
        MAX_N_UNSIGNED = 2**nbits-1
        nbit_twos_complement = make_twos_complement_converter(nbits)

    SIGN_BIT_MASK = MAX_N_SIGNED+1

    def interpret_nbits_as_signed(value):
        # does this perform better than value > MAX_N_SIGNED?
        if value & SIGN_BIT_MASK: # check for sign bit
            return nbit_twos_complement(value)
        else:
            return value

    def register_nbit_negative(register_file, reg0):
        return register_file[reg0] & SIGN_BIT_MASK

    def register_nbit_positive(register_file, reg0):
        return not (register_file[reg0] & SIGN_BIT_MASK)


    # 1 OP

    def TRUE_N_BITS(vm, c):
        register_file, reg0, next_ip = get_args_for_1OP(vm, c)
        register_file[reg0] = MAX_N_UNSIGNED
        return next_ip


    # 3 OP

    def CMP_N_BITS(vm, c):
        registerfile, reg0, reg1, reg2, next_ip = get_args_for_3OP(vm, c)
        tmp1 = interpret_nbits_as_signed(registerfile[reg1])
        tmp2 = interpret_nbits_as_signed(registerfile[reg2])
        set_comparison_flags(tmp1, tmp2, registerfile, reg0)
        return next_ip


    # 1 OP immediate

    def JUMP_P_N_BITS(vm, c):
        register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
        if register_negative(register_file, reg0):
            return next_ip
        else: # positive
            return next_ip + raw_immediate

    def JUMP_NP_N_BITS(vm, c):
        register_file, reg0, raw_immediate, next_ip = get_args_for_1OPI(vm, c)
        if register_negative(register_file, reg0):
            return next_ip + raw_immediate
        else: # positive
            return next_ip

    return {
        ('TRUE_%d' % nbits): TRUE_N_BITS,
        ('CMP_%d' % nbits): CMP_N_BITS,
        ('JUMP_P_%d' % nbits): JUMP_P_N_BITS,
        ('JUMP_NP_%d' % nbits): JUMP_NP_N_BITS,
    }
