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

from hex0tobin import write_binary_filefd_from_hex0_filefd

from .hexcommon import (
    Hex256SumMatch, HexCommon, Encoding_rom_256_Common,
    make_get_sha256sum_of_file_after_encode
    )
from .test_hex1tobin import get_sha256sum_of_file_after_hex1_encode
from .stage0 import (
    STAGE_0_HEX1_ASSEMBLER_FILEPATH,
    STAGE_0_HEX2_ASSEMBLER_FILEPATH,
    )

class Hex2Common(HexCommon):
    encoding_rom_filename = STAGE_0_HEX1_ASSEMBLER_FILEPATH
    rom_encode_func = staticmethod(write_binary_filefd_from_hex0_filefd)

class Test_hex_assembler1_256Sum(Hex2Common, Encoding_rom_256_Common):
    sha256sumfilename = 'roms/stage1_assembler-1'

class Test_hex_assember2_256Sum(Hex2Common, Hex256SumMatch):
    sha256sumfilename = 'roms/stage1_assembler-2'

    def compute_sha256_digest(self):
        return get_sha256sum_of_file_after_hex1_encode(
            STAGE_0_HEX2_ASSEMBLER_FILEPATH)
