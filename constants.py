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

TAPEFD_I_STDIN, TAPEFD_I_STDOUT = 2, 3
