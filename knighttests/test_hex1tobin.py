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

from unittest import skipIf

from hex0tobin import (
    write_binary_filefd_from_hex0_filefd,
    int_bytes_from_hex0_fd,
    )
from hex1tobin import (
    write_binary_filefd_from_hex1_filefd,
    )

from .hexcommon import (
    HexCommon, Encoding_rom_256_Common,
    make_get_sha256sum_of_file_after_encode,
    TestHexKnightExecuteCommon,
    CommonStage1HexEncode,
)
from .stage0 import (
    STAGE_0_HEX1_ASSEMBLER_FILEPATH,
    STAGE_0_HEX2_ASSEMBLER_RELATIVE_PATH,
    )
from .util import make_optimize_and_register_size_variations

from constants import MEM

get_sha256sum_of_file_after_hex1_encode = \
    make_get_sha256sum_of_file_after_encode(
        write_binary_filefd_from_hex1_filefd)

class Test_hex_assembler1_ROM_256Sum(HexCommon, Encoding_rom_256_Common):
    encoding_rom_filename = STAGE_0_HEX1_ASSEMBLER_FILEPATH
    rom_encode_func = staticmethod(write_binary_filefd_from_hex0_filefd)
    sha256sumfilename = 'roms/stage1_assembler-1'

class TestStage1Hex1Encode(CommonStage1HexEncode, TestHexKnightExecuteCommon):
    encoding_rom_filename = STAGE_0_HEX1_ASSEMBLER_FILEPATH
    rom_encode_func = staticmethod(write_binary_filefd_from_hex0_filefd)
    int_bytes_from_rom_encode_file = staticmethod(int_bytes_from_hex0_fd)

    #  setUp and tearDown come from TestHexKnightExecuteCommon

    def test_encode_stage1_hex2_with_stage1_hex1(self):
        self.execute_test_hex_load_published_sha256(
            STAGE_0_HEX2_ASSEMBLER_RELATIVE_PATH,
            "roms/stage1_assembler-2",
    )

(TestStage1Hex1Encode32Optimize,
 TestStage1Hex1Encode64,
 TestStage1Hex1Encode64Optimize,
 TestStage1Hex1Encode16,
 TestStage1Hex1Encode16Optimize,
 ) = make_optimize_and_register_size_variations(TestStage1Hex1Encode)
