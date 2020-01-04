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

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

(IP, REG, MEM, HALTED, EXCEPT, PERF_COUNT,
 TAPE1FILENAME, TAPE2FILENAME, TAPEFD) = range(9)
(OP, RAW, CURIP, NEXTIP, RESTOF, INVALID,
 RAW_XOP, XOP, RAW_IMMEDIATE, IMMEDIATE, I_REGISTERS, HAL_CODE) = range(12)

(CONDITION_BIT_C, CONDITION_BIT_B, CONDITION_BIT_O,
 CONDITION_BIT_GT, CONDITION_BIT_EQ, CONDITION_BIT_LT) = [
     1<<(6-i-1)
     for i in range(6)]

HALT_OP = 0xFF
HAL_CODE_OP = 0x42
HAL_CODE_FCLOSE = 0x100002
HAL_CODE_FGETC = 0x100100
HAL_CODE_FPUTC = 0x100200
HAL_CODE_FOPEN_WRITE = 0x100001

HAL_IO_DATA_REGISTER, HAL_IO_DEVICE_REGISTER = (0,1)
HAL_IO_DEVICE_STDIO = 0x0

TAPEFD_I_STDIN, TAPEFD_I_STDOUT = 2, 3

ARRAY_TYPE_UNSIGNED_CHAR = 'B'
ARRAY_TYPE_UNSIGNED_SHORT = 'H'
ARRAY_TYPE_UNSIGNED_INT = 'I'
ARRAY_TYPE_UNSIGNED_INT_LONG = 'L'
ARRAY_TYPE_UNSIGNED_LONG_LONG = 'Q'
