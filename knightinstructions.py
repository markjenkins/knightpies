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

def READPC(vm, c):
    pass

def READSCID(vm, c):
    pass

def FALSE(vm, c):
    pass

def TRUE(vm, c):
    pass

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
    pass

def LOADUI(vm, c):
    pass

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
