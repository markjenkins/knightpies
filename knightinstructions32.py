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

nbit_optimized_dict = make_nbit_optimized_functions(32)

# 1 OP
TRUE = nbit_optimized_dict['TRUE_32']


# 3 OP
CMP = nbit_optimized_dict['CMP_32']


# 1 OP immediate
JUMP_P = nbit_optimized_dict['JUMP_P_32']
JUMP_NP = nbit_optimized_dict['JUMP_NP_32']
