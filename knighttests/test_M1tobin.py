# Copyright (C) 2020 Mark Jenkins <mark@markjenkins.ca>
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

from .stage0 import STAGE_0_HEX2_ASSEMBLER_FILEPATH

from .hexcommon import (
    Hex256SumMatch, HexCommon, Encoding_rom_256_Common,
    )

from stage0dir import get_stage0_file
from hex1tobin import write_binary_filefd_from_hex1_filefd

from .test_hex2tobin import (
    get_sha256sum_of_file_after_hex2_encode,
    )

class M1Common(HexCommon):
    encoding_rom_filename = get_stage0_file(STAGE_0_HEX2_ASSEMBLER_FILEPATH)
    rom_encode_func = staticmethod(write_binary_filefd_from_hex1_filefd)

class Test_hex_assembler2_256Sum(M1Common, Encoding_rom_256_Common):
    sha256sumfilename = 'roms/stage1_assembler-2'

class Test_M0_256Sum(M1Common, Hex256SumMatch):
    sha256sumfilename = 'roms/M0'

    def compute_sha256_digest(self):
        return get_sha256sum_of_file_after_hex2_encode(
            get_stage0_file('stage1/M0-macro.hex2'))
