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

from stage0dir import get_stage0_file

STAGE_0_MONITOR_RELATIVE_PATH = 'stage0/stage0_monitor.hex0'

STAGE_0_MONITOR_HEX_FILEPATH = get_stage0_file(STAGE_0_MONITOR_RELATIVE_PATH)

STAGE_0_HEX0_ASSEMBLER_RELATIVE_PATH = 'stage1/stage1_assembler-0.hex0'

STAGE_0_HEX0_ASSEMBLER_FILEPATH = get_stage0_file(
    STAGE_0_HEX0_ASSEMBLER_RELATIVE_PATH)
